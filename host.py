from server import Server
from game_engine import Engine
from typing import Callable, Any
from game_map import Map, MAP1
from pieces import Piece


class Host:
    def __init__(self, server_: Server, engine: Engine):
        server_.main()
        self.server = server_
        self.engine = engine
        self.server.up = self.check_submissions
        self.update()

    def close(self):
        """
        ends socket connection
        """
        self.server.close()


    def submit(self, method: str, *args, **kwargs) -> Any:
        """
        submits request to game engine
        :param method: method name
        :param args: arguments
        :param kwargs: keyword arguments
        :return: method return
        """
        try:
            return self.engine.__getattribute__(method)(*args, **kwargs)
        except AttributeError as error:
            print(error.__str__())
            return False

    def check_submissions(self) -> Any:
        """
        checks for submitted data
        """
        print('checking for submissions')
        # print(self.server.player_msg)
        if self.engine.setup:
            if blue_data := self.server.blue_msg:
                try:
                    self.submit(blue_data[0], *blue_data[1:])
                    self.update()
                    self.server.send_all()
                except IndexError:
                    print('ERROR!:')
                    print(blue_data)
                    print()
            if red_data := self.server.red_msg:
                try:
                    self.submit(red_data[0], *red_data[1:])
                    self.update()
                    self.server.send_all()
                except IndexError:
                    print('ERROR!:')
                    print(red_data)
                    print()
            self.server.player_msg = {}
        elif data := self.server[self.engine.turn]:
            print(f"{self.engine.turn} has submitted:")
            # print(data)
            try:
                self.submit(data[0], *data[1:])
                self.update()
                self.server.send_all()
            except IndexError:
                print('ERROR!:')
                print(data)
                print()
            self.server.player_msg = {}

    def update(self):
        self.server.data = self.engine.data


if __name__ == '__main__':
    ENG = Engine(MAP1)

    # ENG.pieces = [Piece('7', (1, 2), color='Red'),
    #               Piece('3', (4, 2), color='Red'),
    #               Piece('10', (9, 5), color='Blue'),
    #               Piece('M', (3, 7), color='Blue'),
    #               Piece('6', (2, 2), color='Red'),
    #               Piece('9', (2, 1), color='Red'),
    #               Piece('10', (3, 1), color='Red'),
    #               Piece('4', (5, 1), color='Red'),
    #               Piece('S', (8, 2), color='Red'),
    #               Piece('1', (9, 2), color='Red'),
    #               Piece('2', (5, 2), color='Red'),
    #               Piece('2', (7, 2), color='Red'),
    #               Piece('2', (7, 1), color='Red'),
    #               Piece('2', (6, 1), color='Red'),
    #               Piece('1', (0, 2), color='Red'),
    #               Piece('M', (9, 0), color='Red'),
    #               Piece('M', (3, 2), color='Red'),
    #               Piece('M', (8, 0), color='Red'),
    #               Piece('M', (7, 0), color='Red'),
    #               Piece('M', (6, 0), color='Red'),
    #               Piece('F', (0, 0), color='Red'),
    #               Piece('3', (1, 1), color='Red'),
    #               Piece('3', (0, 1), color='Red'),
    #               Piece('2', (4, 1), color='Red'),
    #               Piece('2', (6, 2), color='Red'),
    #               Piece('3', (8, 1), color='Red'),
    #               Piece('3', (9, 1), color='Red'),
    #               Piece('4', (5, 0), color='Red'),
    #               Piece('5', (4, 0), color='Red'),
    #               Piece('5', (3, 0), color='Red'),
    #               Piece('6', (2, 0), color='Red'),
    #               Piece('8', (1, 0), color='Red'),
    #               Piece('1', (8, 5), color='Blue'),
    #               Piece('1', (0, 5), color='Blue'),
    #               Piece('S', (1, 5), color='Blue'),
    #               Piece('M', (9, 6), color='Blue'),
    #               Piece('M', (8, 7), color='Blue'),
    #               Piece('F', (9, 7), color='Blue'),
    #               Piece('7', (5, 5), color='Blue'),
    #               Piece('6', (4, 5), color='Blue'),
    #               Piece('6', (3, 5), color='Blue'),
    #               Piece('5', (2, 5), color='Blue'),
    #               Piece('5', (6, 5), color='Blue'),
    #               Piece('4', (7, 5), color='Blue'),
    #               Piece('3', (7, 6), color='Blue'),
    #               Piece('3', (8, 6), color='Blue'),
    #               Piece('3', (7, 7), color='Blue'),
    #               Piece('3', (6, 6), color='Blue'),
    #               Piece('3', (6, 7), color='Blue'),
    #               Piece('2', (5, 6), color='Blue'),
    #               Piece('2', (5, 7), color='Blue'),
    #               Piece('2', (4, 6), color='Blue'),
    #               Piece('2', (4, 7), color='Blue'),
    #               Piece('2', (3, 6), color='Blue'),
    #               Piece('4', (2, 6), color='Blue'),
    #               Piece('2', (1, 6), color='Blue'),
    #               Piece('8', (0, 6), color='Blue'),
    #               Piece('9', (0, 7), color='Blue'),
    #               Piece('M', (1, 7), color='Blue'),]
                  # Piece('M', (2, 7), color='Blue')]

    G = Host(Server(5555), ENG)

    while True:
        nums = input("Enter multiple numbers: ")
        try:
            G.server.data = tuple([int(i) for i in nums.split(' ')])
            G.server.send_all()
            print(G.server.data)
        except SyntaxError as e:
            print(e.msg)
        except ValueError as e:
            print(e.__traceback__.tb_frame.f_trace)
