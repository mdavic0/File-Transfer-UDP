import logging
import threading
from .constants import *

NOT_ACKED = False
ACKED = True


class Window():
    def __init__(self, event):
        self.packets = {}
        self.event = event
        self.lock = threading.Lock()
        self.base_seq = 0
        self.error = False

    def add_sequence_number(self, sequence_number):
        self.lock.acquire(blocking=True)
        self.packets[sequence_number] = NOT_ACKED
        self.lock.release()

    def is_full(self):
        with self.lock:
            return len(self.packets) > MAX_WINDOW_SIZE

    def is_acked(self, sequence_number):
        # self.lock.acquire(blocking = True)
        return self.packets[sequence_number]
        # self.lock.release()

    def update(self):
        was_updated = False
        # logging.error(f"Window size is : {len(self.packets)}")
        self.lock.acquire(blocking=True)
        while len(self.packets) > 0 and self.packets[self.base_seq]:
            self.packets.pop(self.base_seq)
            was_updated = True
            self.base_seq += 1

        if was_updated:
            self.event.set()
        self.lock.release()

    def is_empty(self):
        return len(self.packets) == 0

    def acknowledge_packet(self, sequence_number):
        self.lock.acquire(blocking=True)
        self.packets[sequence_number] = ACKED
        self.lock.release()

    def connection_lost(self):
        with self.lock:
            return self.error

    def notify_error_connection(self):
        with self.lock:
            self.event.set()

            self.error = True
