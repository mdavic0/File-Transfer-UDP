import logging
import os
from lib.constants import PAYLOAD_SIZE


class FileManager:
    def __init__(self, path, mode):
        self.path = path
        self.src = path
        self.read_now = None
        self.read_previous = None
        self.file = open(path, mode)

    def read(self):
        try:
            return self.file.read(PAYLOAD_SIZE)
        except Exception as e:
            logging.error(f'Error reading file {self.src}, error: {e}')

    def write(self, content):
        self.file.write(content)

    def get_file_size(self):
        return os.path.getsize(self.path)

    def close(self):
        self.file.close()
