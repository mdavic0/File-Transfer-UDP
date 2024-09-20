from socket import socket, SOCK_DGRAM, AF_INET
from lib.selective_repeat import SelectiveRepeat
from .constants import (DOWNLOAD, UPLOAD, MODE_WRITE, MODE_READ,
                        MAX_RETRIES, TIMEOUT_SECONDS, MAX_SIZE_PACKET)
from .file_manager import FileManager
import logging
import struct
from .packet import Packet
from .stop_and_wait import StopAndWait
from .exceptions import ConnectionFailedError, FileNotInServerError


class Client:
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.server_address = (self.host, self.port)
        self.skt = socket(AF_INET, SOCK_DGRAM)

        if args.mininet:
            self.skt.bind(('', self.port))

        self.filename = args.name
        self.src = args.src
        self.dst = f'{args.dst}/{self.filename}'
        self.action = DOWNLOAD  # default
        self.protocol = SelectiveRepeat(
            self.skt, self.server_address) if args.protocol else StopAndWait(
            self.skt, self.server_address)
        self.protocol_code = args.protocol

    def download(self):
        self.action = DOWNLOAD

        try:
            logging.info("About to resolve handshake")
            self.resolve_handshake()
            logging.info("Finished handshake")
        except FileNotInServerError as e:
            logging.error(e)
            return

        file = FileManager(self.dst, MODE_WRITE)

        self.protocol.receive_file(file)

    def upload(self):
        self.action = UPLOAD

        try:
            file = FileManager(self.src, MODE_READ)
        except FileNotFoundError as e:
            logging.error(e)
            return

        self.resolve_handshake()

        logging.info("Finished handshake")

        self.protocol.send_file(file)

    def send_bytes(self, data):
        msg = bytes([0, 0, 0, 0, 0, 0]) + struct.pack("I", 0) + \
            struct.pack("H", len(data)) + data
        self.send(msg)
        logging.info("Se envio data exitosamente")

    def send_handshake(self):
        if self.action == UPLOAD:
            file_name = self.filename
            logging.info(
                f"El nombre del archivo que se quiere subir: {file_name}")

        else:

            file_name = self.src
            logging.info(
                f"El nombre del archivo a descargar es: {file_name}")

        length = len(file_name)
        logging.info("About to encode message")

        msg = bytes([1, 0, self.action, self.protocol_code, 0, 0]) + \
            struct.pack("I", 0) + struct.pack("H", length) + file_name.encode()

        logging.info("Finished encoding message")
        self.send(msg)
        logging.info(
            "Sent Handshake: '{}' to server address: {}".format(
                msg, self.server_address))

    def send(self, message, address=None):
        if address:
            self.skt.sendto(message, address)
        else:
            self.skt.sendto(message, (self.host, self.port))

    def resolve_handshake(self):

        retries = 0
        while retries < MAX_RETRIES:
            self.send_handshake()
            try:
                self.skt.settimeout(TIMEOUT_SECONDS)
                response, self.server_address = self.skt.recvfrom(
                    MAX_SIZE_PACKET)
                self.skt.settimeout(None)

                packet = Packet(response)

                if packet.error:
                    self.send_ack()
                    raise FileNotInServerError

                return
            except TimeoutError:
                retries += 1
                logging.info("Hubo un timeout")

        raise ConnectionFailedError

    def send_ack(self):
        message = bytes([0, 1, 0, 0, 0, 0]) + \
            struct.pack("I", 0) + struct.pack("H", 0)
        self.skt.sendto(message, self.server_address)
