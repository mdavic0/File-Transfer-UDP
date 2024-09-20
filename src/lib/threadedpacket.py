import logging
import threading
import struct
from queue import Queue, Empty

from lib.constants import *


class ThreadedPacket(threading.Thread):
    def __init__(
            self,
            sequence_number,
            data,
            queue,
            protocolo,
            window,
            address):
        threading.Thread.__init__(self)
        self.sequence_number = sequence_number
        self.payload = data
        self.is_alive = True
        self.was_acknowledged = False
        self.queue = queue
        self.protocol = protocolo
        self.lock = threading.Lock()
        self.window = window
        self.address = address

    def create_packet(
            data,
            sequence_number,
            queue,
            protocolo,
            window,
            address):

        return ThreadedPacket(
            sequence_number,
            data,
            queue,
            protocolo,
            window,
            address)

    def send_data(self, data, sequence_number):

        msg = bytes([0, 0, 0, 0, 0, 0]) + struct.pack("I",
                                                      sequence_number) + struct.pack("H", len(data)) + data
        self.protocol.sendto(msg, self.address)
        # logging.info(f"Data sent, sequence number: {sequence_number}")

    def run(self):
        self.send_data(self.payload, self.sequence_number)
        logging.info(f"[New Payload Sent] Sequence Number {self.sequence_number}")

        retries = 0
        while retries < MAX_RETRIES:
            try:
                message = self.queue.get(block=True, timeout=TIMEOUT_SECONDS)
                logging.info(f"[ACK Received] Sequence Number: {self.sequence_number}")
                self.set_acknowledged()
                self.window.acknowledge_packet(self.sequence_number)
                self.window.update()
                return
            except Empty:
                logging.info(f"[Payload Resent] Sequence Number: {self.sequence_number}")
                self.send_data(self.payload, self.sequence_number)
                retries += 1

        self.window.notify_error_connection()
        logging.warning(f"[Timeout] Sequence Number: {self.sequence_number}")
        self.is_alive = False

    def set_acknowledged(self):
        # self.lock.acquire(blocking=True)
        if self.is_alive:
            self.was_acknowledged = True
        # self.lock.release()

    def get_acknowledged(self):
        return self.was_acknowledged

    def connection_lost(self):
        return not self.is_alive
