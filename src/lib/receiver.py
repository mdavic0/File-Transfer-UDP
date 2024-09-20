import logging
from queue import Empty
import threading
from lib.constants import (TIMEOUT_SECONDS, MAX_SIZE_PACKET, MAX_RETRIES)
from lib.packet import Packet

ACKED = 1


class Receiver(threading.Thread):
    def __init__(self, socket, window, msg_queue=None):
        threading.Thread.__init__(self)
        self.ack_receivers = {}
        self.packets = {}
        self.socket = socket
        self.window = window
        self.error = False
        self.is_dead = False
        self.msg_queue = msg_queue

    def receive_data(self):
        if self.msg_queue:
            message = self.msg_queue.get(block=True, timeout=TIMEOUT_SECONDS)
        else:
            self.socket.settimeout(TIMEOUT_SECONDS)
            message, _ = self.socket.recvfrom(MAX_SIZE_PACKET)
            self.socket.settimeout(None)

        self.retries = 0
        return message

    def add_packet(self, packet, queue):
        self.ack_receivers[packet.sequence_number] = queue
        self.packets[packet.sequence_number] = packet

    def kill(self):
        self.is_dead = True

    def run(self):
        retries = 0
        while retries < MAX_RETRIES and not self.is_dead:
            try:
                data = self.receive_data()

                message = Packet(data)

                if message.fin:
                    return

                if message.ack:
                    if message.sequence_number in self.ack_receivers:
                        self.ack_receivers[message.sequence_number].put(ACKED)

                        self.packets[message.sequence_number].join()
                        del self.ack_receivers[message.sequence_number]
                        del self.packets[message.sequence_number]

                retries = 0
            except (TimeoutError, Empty):
                error = self.window.connection_lost()
                if error:
                    logging.warning("[ThreadedPacket] Timeout")
                    break
                retries += 1

        self.is_dead = True

    def connection_dead(self):
        return self.is_dead
