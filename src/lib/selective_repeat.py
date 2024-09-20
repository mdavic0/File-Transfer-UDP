import logging
from queue import Empty, Queue
import struct
from threading import Event
from lib.constants import MAX_RETRIES, TIMEOUT_SECONDS, MAX_SIZE_PACKET
from lib.exceptions import TimeoutMaxRetriesError
from lib.packet import Packet
from lib.receiver import Receiver
from lib.threadedpacket import ThreadedPacket
from lib.window import Window


class SelectiveRepeat():
    def __init__(self, skt, address):
        self.socket = skt
        self.address = address
        self.retries = 0
        self.sequence_number = 0

    def send_data(self, data, sequence_number):

        if self.retries > MAX_RETRIES:
            logging.error("Max retries reached")
            raise TimeoutMaxRetriesError

        packed_seq = struct.pack("I", sequence_number)
        packed_len = struct.pack("H", len(data))
        msg = bytes([0, 0, 0, 0, 0, 0]) + packed_seq + packed_len + data

        self.socket.sendto(msg, self.address)
        logging.info("Data sent, sequence number: ".format(
            sequence_number))

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
        logging.info(f"ACK sent, seq number: {sequence_number}")

    def send_file(self, file, msg_queue=None):
        logging.info("Opening file")
        data = file.read()
        event = Event()  # Si se desliza la window, o si se murio un cliente
        window = Window(event)
        receiver = Receiver(self.socket, window, msg_queue)
        receiver.start()
        while data:

            if window.is_full():
                event.wait(timeout=TIMEOUT_SECONDS)
                event.clear()
                if window.connection_lost():
                    logging.error("Error de conexion con cliente")
                    return
            queue = Queue()

            packet = ThreadedPacket.create_packet(
                data, self.sequence_number, queue, self.socket, window, self.address)

            window.add_sequence_number(packet.sequence_number)
            receiver.add_packet(packet, queue)

            packet.start()

            self.sequence_number += 1

            data = file.read()

        while not window.is_empty():
            window.update()
            continue

        receiver.kill()
        receiver.join()

        self.resolve_send_fin(self.address, msg_queue)
        file.close()
        receiver.join()

        logging.info("File sent")

    def receive_file(self, file, msg_queue=None):
        base_seq = 0
        received_packets = {}

        self.retries = 0
        logging.info("Receiving file using Selective repeat")
        while self.retries < MAX_RETRIES:
            try:

                message = self.receive_data(msg_queue)
                packet = Packet(message)

                if packet.fin:
                    self.resolve_receive_fin(self.address, msg_queue)

                    file.close()
                    logging.info(f"File received")
                    return

                self.send_ack(packet.sequence_number)

                if not packet.ack and packet.sequence_number < base_seq:
                    logging.info(f"[Duplicate Received] Sequence Number: {packet.sequence_number}")
                    raise TimeoutError

                if packet.sequence_number not in received_packets:
                    received_packets[packet.sequence_number] = packet.payload

                logging.info(f"[New Payload Received] Sequence Number: {packet.sequence_number}")
                while len(received_packets) > 0 and base_seq in received_packets:
                    data = received_packets.pop(base_seq)
                    file.write(data)
                    base_seq += 1
                self.retries = 0
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
