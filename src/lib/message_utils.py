from lib.constants import MAX_SIZE_PACKET


def receive_msg_encoded(socket):
    msg, _ = socket.recvfrom(1024)
    return msg


def receive_msg(msg_queue, socket, timeout=None):
    if msg_queue:
        maybe_ack = msg_queue.get(block=True, timeout=timeout)
    else:
        maybe_ack, _ = socket.recvfrom(MAX_SIZE_PACKET)
    return maybe_ack
