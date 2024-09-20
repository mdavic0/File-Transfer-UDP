import struct
import time
from socket import *
import logging
from threading import Thread
from queue import Queue, Empty
import traceback

from lib.selective_repeat import SelectiveRepeat
from .stop_and_wait import StopAndWait
from .packet import Packet
from .constants import *
from .file_manager import FileManager


class Server:
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.client_queues = {}
        self.clients = {}
        storage = args.storage
        # Camniar directorio por defecto
        self.storage = storage if storage is not None else "/tmp"
        self.skt = socket(AF_INET, SOCK_DGRAM)

    def start(self):
        self.skt.bind((self.host, self.port))
        logging.info(f"Server started at {self.host}:{self.port}")
        try:
            self.handle_messages()
        except Exception as e:
            print(f"An error occurred: {e}")

            raise e

    def handle_messages(self):
        while True:
            encoded_msg, addr_client = self.skt.recvfrom(MAX_SIZE_PACKET)
            data = Packet(encoded_msg)

            if addr_client not in self.clients and not data.syn:
                continue

            if addr_client not in self.clients:
                client_queue = Queue()
                self.client_queues[addr_client] = client_queue

                args = (client_queue, addr_client)
                client = Thread(target=self.handle_new_client, args=args)
                self.clients[addr_client] = client
                client.start()

            self.client_queues[addr_client].put(encoded_msg)

    def handle_new_client(self, client_queue, client_address):
        logging.info(f"Started new thread to handle client {client_address}")

        encoded_msg = client_queue.get(block=True, timeout=TIMEOUT_SECONDS)
        data = Packet(encoded_msg)

        transfer_socket = socket(AF_INET, SOCK_DGRAM)
        if data.protocol:
            logging.info(
                f"Using Selective Repeat for client : {client_address}")
            protocol = SelectiveRepeat(transfer_socket, client_address)

        else:
            logging.info(f"Using Stop and Wait for client : {client_address}")
            protocol = StopAndWait(transfer_socket, client_address)

        file_path = f"{self.storage}/{data.payload.decode('utf-8')}"

        try:
            if data.action == UPLOAD:
                file = FileManager(file_path, MODE_WRITE)

                # Wait for client to ack
                self.resolve_handshake(client_address, client_queue)
                self.handle_upload(
                    file, client_queue, client_address, protocol)

            elif data.action == DOWNLOAD:
                file = FileManager(file_path, MODE_READ)

                # Send 1 ACK and start sending the file
                self.send_ack(client_address)
                self.handle_download(
                    file, client_queue, client_address, protocol)

            else:
                logging.error(f"La accion {data.action} enviada no existe")

        except FileNotFoundError as e:
            logging.error(e)
            self.send_error(client_address, client_queue)
            return

        except Exception as e:
            logging.error(f"Couldn't establish connection with {client_address}, error: {e}")
            return

    def send_error(self, addr_client, client_queue):
        retries = 0
        while retries < MAX_RETRIES:
            message = bytes([1, 1, 0, 0, 0, 1]) + \
                struct.pack("I", 0) + struct.pack("H", 0)
            self.skt.sendto(message, addr_client)
            try:
                response = client_queue.get(
                    block=True, timeout=TIMEOUT_SECONDS)
                return
            except Empty:
                retries += 1

    def send_ack(self, addr_client):
        message = bytes([1, 1, 0, 0, 0, 0]) + \
            struct.pack("I", 0) + struct.pack("H", 0)
        self.skt.sendto(message, addr_client)

    def handle_upload(self, file, client_queue, client_address, protocol):

        protocol.receive_file(file, client_queue)

        self.close_client_connection(client_address)

    def handle_download(self, file, client_queue, client_address, protocol):

        protocol.send_file(file, client_queue)

        self.close_client_connection(client_address)

    def close_client_connection(self, client_address):
        del self.client_queues[client_address]
        del self.clients[client_address]

    def resolve_handshake(self, client_address, client_queue):
        retries = 0
        while retries < MAX_RETRIES:
            self.send_ack(client_address)
            try:
                response = client_queue.get(
                    block=True, timeout=TIMEOUT_SECONDS)
                return
            except Empty:
                retries += 1
        raise Exception

    def quit(self):
        for client_queue in self.client_queues:
            self.client_queues[client_queue].join()
        for client in self.clients:
            self.clients[client].join()
