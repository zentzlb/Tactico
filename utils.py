from typing import Callable, Any
import socket
import pickle


def transmitter_protocol(sock: socket.socket, data: Any):
    """
    protocol for sending data across socket connection
    :param sock: socket
    :param data: data to send
    """
    try:
        sock.sendall(data + b'%')
    except ConnectionAbortedError:
        print('Connection Aborted')
    except OSError:
        print('Socket Closed')


def receiver_protocol(sock: socket.socket) -> Any:
    """
    protocol for sending data across socket connection
    :param sock: socket
    :return: received data
    """
    try:
        package = b''
        while not package.endswith(b'%'):
            package += sock.recv(2048)
        try:
            return pickle.loads(package[:-1])
        except pickle.UnpicklingError:
            try:
                return package.decode("utf-8")[:-1]
            except UnicodeDecodeError:
                print('Corrupted Data')
    except ConnectionAbortedError:
        print('Connection Aborted')

