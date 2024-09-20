import struct
from .constants import *
from .exceptions import *
from .file_manager import FileManager
from .message_utils import *
from .packet import Packet
import logging
from queue import Queue, Empty


class StopAndWait:
    def __init__(self, skt, address):
        self.socket = skt
        self.address = address
        self.retries = 0
        self.sequence_number = 0

    def send_data(self, data, sequence_number):
        if self.retries > MAX_RETRIES:
            logging.error("Max retries reached")
            raise TimeoutMaxRetriesError

        msg = bytes([0, 0, 0, 0, 0, 0]) + struct.pack("I",
                                                      sequence_number) + struct.pack("H", len(data)) + data
        self.socket.sendto(msg, self.address)

    def receive_data(self, msg_queue=None):
        if msg_queue:
            message = msg_queue.get(block=True, timeout=TIMEOUT_SECONDS)
        else:
            self.socket.settimeout(TIMEOUT_SECONDS)
            message, _ = self.socket.recvfrom(MAX_SIZE_PACKET)
            self.socket.settimeout(None)

        self.retries = 0
        return message

    def send_ack(self, sequence_number):
        msg_ack = bytes([0, 1, 0, 0, 0, 0]) + struct.pack("I",
                                                          sequence_number) + struct.pack("H", 0)
        self.socket.sendto(msg_ack, self.address)
        logging.info(f"[ACK Sent] Sequence Number: {sequence_number}")

    def send_file(self, file, msg_queue=None):

        data = file.read()
        while data:
            try:
                self.send_data(data, self.sequence_number)
                logging.info(f"[Payload Sent] Sequence Number {self.sequence_number}")

                self.socket.settimeout(TIMEOUT_SECONDS)
                message = Packet(
                    receive_msg(
                        msg_queue,
                        self.socket,
                        TIMEOUT_SECONDS))

                if message.sequence_number < self.sequence_number:
                    raise TimeoutError

                logging.info(f"[ACK Received] Sequence Number: {message.sequence_number}")

            except (TimeoutError, Empty):
                self.retries += 1

                continue
            except TimeoutMaxRetriesError:
                file.close()
                raise TimeoutMaxRetriesError

            self.socket.settimeout(None)
            self.sequence_number += 1
            self.retries = 0
            data = file.read()

        file.close()
        self.resolve_send_fin(self.address, msg_queue)
        logging.info("Finished sending file")

    def receive_file(self, file, msg_queue=None):

        self.retries = 0
        while self.retries < MAX_RETRIES:
            try:

                message = self.receive_data(msg_queue)
                packet = Packet(message)

                if packet.fin:
                    self.resolve_receive_fin(self.address, msg_queue)
                    file.close()
                    return

                self.send_ack(packet.sequence_number)

                if not packet.ack and self.sequence_number != packet.sequence_number:
                    logging.info(f"[Duplicate Received] Sequence Number: {packet.sequence_number}")
                    continue

                logging.info(f"[New Payload Received] Sequence Number: {packet.sequence_number}")
                file.write(packet.payload)
                self.sequence_number += 1

            except (TimeoutError, Empty):
                self.retries += 1
                continue

        file.close()
        logging.warning("Connection problem with client")

    def send_fin(self, address):
        msg = bytes([0, 0, 0, 0, 1, 0]) + \
            struct.pack("I", 0) + struct.pack("H", 0)
        self.socket.sendto(msg, address)

    def send_fin_ack(self, address):
        msg = bytes([0, 1, 0, 0, 1, 0]) + \
            struct.pack("I", 0) + struct.pack("H", 0)
        self.socket.sendto(msg, address)

    def resolve_receive_fin(self, address, msg_queue):
        self.socket.settimeout(TIMEOUT_SECONDS)
        retries = 0
        while retries < MAX_RETRIES:
            self.send_fin_ack(address)
            try:
                message = self.receive_data(msg_queue)
                packet = Packet(message)
                if (packet.fin and packet.ack):
                    return
                continue
            except (TimeoutError, Empty):
                retries += 1

    def resolve_send_fin(self, address, msg_queue):
        self.socket.settimeout(TIMEOUT_SECONDS)
        retries = 0
        while retries < MAX_RETRIES:
            self.send_fin(address)
            try:
                message = self.receive_data(msg_queue)
                packet = Packet(message)
                if (packet.fin and packet.ack):
                    return
                continue
            except (TimeoutError, Empty):
                retries += 1
        raise Exception
