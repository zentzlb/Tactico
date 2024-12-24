import pickle
import socket
from _thread import start_new_thread, exit
import time
import sys
from typing import Callable, Any
from utils import transmitter_protocol, receiver_protocol


class Server:

    def __init__(self, port: int, up: Callable = lambda: print('up function triggered')):
        self.players = {'Red': dict(),
                        'Blue': dict()}
        self.player_msg = {}
        self.data = None
        self.up = up
        self.port = port
        self.host = socket.gethostbyname(socket.gethostname())
        # self.update_time = time.time()
        self.run = True
        print(self.host)

    def close(self):
        self.run = False
        raise SystemExit

    def reset(self):
        self.players = {'Red': dict(),
                        'Blue': dict()}
        self.player_msg = {}
        self.data = None

    @property
    def pickled_data(self) -> Any:
        return pickle.dumps(self.data)

    @property
    def red_msg(self) -> Any:
        """
        message from red player
        :return: message from Red
        """
        if self.players['Red'] and (addr := self.players['Red']['addr']) in self.player_msg:
            return self.player_msg[addr]

    @property
    def blue_msg(self) -> Any:
        """
        message from blue player
        :return: message from Blue
        """
        if self.players['Blue'] and (addr := self.players['Blue']['addr']) in self.player_msg:
            return self.player_msg[addr]

    def __getitem__(self, item: str):
        if (addr := self.players[item]['addr']) in self.player_msg:
            return self.player_msg[addr]

    def main(self):
        """
        initiates Server
        """
        start_new_thread(self.connect, tuple())

    def assign_player(self, conn: socket.socket, addr: tuple[str, int]) -> str:
        """
        assigns player to either 'Red' or 'Blue' role
        :return: player color
        """
        if not self.players['Red']:
            self.players['Red'] = {'conn': conn, 'addr': addr}
            return 'Red'
        elif not self.players['Blue']:
            self.players['Blue'] = {'conn': conn, 'addr': addr}
            return 'Blue'
        print('error in player assignment')
        return ''

    def connect(self):
        """
        look for connections
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen()
            while self.run:
                if not (self.players['Red'] and self.players['Blue']):
                    try:
                        conn, addr = sock.accept()
                        if addr in self.players.values():
                            time.sleep(0.1)
                            conn.close()
                            print('Player Already Connected')
                        else:
                            color = self.assign_player(conn, addr)
                            transmitter_protocol(conn, color.encode())
                            transmitter_protocol(conn, self.pickled_data)
                            print(f"\nConnected to: {addr}")
                            start_new_thread(self.threaded_client, (conn, addr, color))
                    except OSError as error:
                        print(error)

    def receive(self, conn: socket.socket, addr: tuple[str, int]) -> Any:
        """
        handles incoming messages from client
        :param conn: connected client socket
        :param addr: client address
        :return: object
        """
        while True:

            try:
                self.player_msg[addr] = receiver_protocol(conn)
                self.up()
                print(self.player_msg[addr])
            except EOFError:
                print('EOF error, get help')
                return
            except ConnectionResetError as error:
                print(error)
                return

    def send_all(self):
        """
        sends pickled data to all connected clients
        """
        for color, player in self.players.items():
            if 'conn' in player and 'addr' in player:
                conn = player['conn']
                addr = player['addr']
                try:
                    transmitter_protocol(conn, self.pickled_data)
                except ConnectionResetError as error:
                    self.players[color] = dict()
                    if addr in self.player_msg:
                        self.player_msg.pop(addr)
                    print(error.__cause__)
                    print(f'Connection to {addr} Lost -> Closing Thread')
                    print(self.players)
                    return

    def threaded_client(self, conn: socket.socket, addr: tuple[str, int], color: str):
        """
        handles incoming and outgoing communication to client
        :param conn: socket connection
        :param addr: address
        :param color: player color
        """

        # print(f'Connection to {addr} Established -> Starting Thread')
        print('Starting Thread')

        print(self.players)

        run = True
        with conn:
            # start_new_thread(self.receive, (conn, addr))
            while run:
                try:
                    self.player_msg[addr] = receiver_protocol(conn)
                    print(self.player_msg[addr])
                    self.up()

                except (ConnectionResetError, ConnectionAbortedError) as error:
                    self.players[color] = dict()
                    if addr in self.player_msg:
                        self.player_msg.pop(addr)
                    print(error.__cause__)
                    print(f'Connection to {addr} Lost -> Closing Thread')
                    print(self.players)
                    return


if __name__ == '__main__':
    r = Server(5555)
    r.data = 'your mom'
    r.main()
    while True:
        nums = input("Enter multiple numbers: ")
        try:
            r.data = tuple([int(i) for i in nums.split(' ')])
            r.send_all()
            print(r.data)
        except SyntaxError as e:
            print(e.msg)
        except ValueError as e:
            print(e.__traceback__.tb_frame.f_trace)
