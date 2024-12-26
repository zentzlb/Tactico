import pickle
from typing import Any, Callable
import socket
import time
from _thread import start_new_thread
from utils import transmitter_protocol, receiver_protocol
import math


class Client:

    def __init__(self, host: str, port: int, up: Callable = lambda: print('up function triggered'),
                 end: Callable = lambda: print('Connection Lost')):

        self.host = host  # The server's hostname or IP address
        self.port = port  # The port used by the server
        self.up = up
        self.end = end
        self.socket: socket.socket | None = None
        self.team = None
        self.data = None
        self.listen = True

    def transmit(self, data: Any) -> bool:
        if self.socket:
            transmitter_protocol(self.socket, pickle.dumps(data))
            return True
        return False

    def close(self):
        self.listen = False
        if self.socket:
            self.socket.close()
        self.socket = None

    def threaded_client(self):
        print('starting')
        run = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while run:
                try:
                    s.connect((self.host, self.port))
                    self.socket = s
                    run = False
                    self.team = receiver_protocol(s)
                    print(self.team)
                    print(s)
                except socket.error as e:
                    print(e)
                    # self.socket = None
                    run = False
                    self.close()
                    # time.sleep(1)
                except EOFError as e:
                    print(e)
                    # self.socket = None
                    time.sleep(1)
                    print('player already connected')
            while self.listen:
                try:
                    self.data = receiver_protocol(s)
                    self.up()
                except (EOFError, ConnectionResetError) as e:
                    print(e)
                    s.close()
                    self.end()
                    self.threaded_client()
                    # return

    def start_thread(self):
        start_new_thread(self.threaded_client, tuple())


if __name__ == '__main__':
    r = Client(socket.gethostbyname('DEEP-BLUE'), 5555)
    r.start_thread()
    while True:
        time.sleep(5)
        r.transmit(f'the time is: {time.time():0.1f}')
        r.close()


