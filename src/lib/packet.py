import struct


class Packet():
    def __init__(self, message):
        self.syn = message[0]
        self.ack = message[1]
        self.action = message[2]
        self.protocol = message[3]
        self.fin = message[4]
        self.error = message[5]
        self.sequence_number = struct.unpack("I", message[6:10])[0]
        self.length = struct.unpack("H", message[10:12])[0]
        self.payload = message[12:12 + self.length]

    def create_packet(data, sequence_number):

        return Packet(bytes([0, 0, 0, 0, 0, 0]) +
                      struct.pack("I", sequence_number) +
                      struct.pack("H", len(data)) +
                      data)
