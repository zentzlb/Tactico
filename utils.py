from typing import Callable, Any
import socket
import pickle
import datetime


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
                transmitter_protocol(sock, 'resend'.encode())
                print('Corrupted Data')
                log_error(package)
    except ConnectionAbortedError:
        print('Connection Aborted')


def log_error(data: bytes):
    with open(f"/error_log/log_{datetime.datetime.today():%H_%M_%S}", "wb") as file:
        file.write(data)


