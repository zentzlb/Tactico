import pickle
import math
from typing import Callable, Self, TypeAlias
from game_types import iPair
import numpy as np


class Obstacle:
    """
    blocker
    """

    def __init__(self, pos: iPair):
        """

        :param pos: position on the board
        """
        self.pos = pos


class Piece:
    """
    game piece
    """
    movement = {'S': 1,
                '1': 1,
                '2': 100,
                '3': 2,
                '4': 1,
                '5': 1,
                '6': 2,
                '7': 2,
                '8': 1,
                '9': 1,
                '10': 1,
                'M': 0,
                'F': 0}

    def __init__(self, rank: str, pos: iPair, color: str = 'Red'):
        """

        :param rank: piece rank
        :param pos: position on the board
        :param color: team color -> 'Red' or 'Blue'
        """
        if rank not in self.movement:
            print('fake rank')
        self.rank = rank
        self.color = color
        self.pos = pos
        self.hidden = True

    @property
    def loc(self) -> np.ndarray:
        """
        piece location
        :return:
        """
        return np.array(self.pos)

    def __in_move(self, x: int, y: int) -> bool:
        """
        check if x and y are in movement range
        :param x: potential x position
        :param y: potential y position
        :return: in movement range
        """
        return (abs(x - self.pos[0]) <= self.movement[self.rank] and
                abs(y - self.pos[1]) <= self.movement[self.rank])

    def __in_range(self, x: int, y: int, x_range: iPair, y_range: iPair):
        """
        check if x and y are in game range
        :param x: potential x position
        :param y: potential y position
        :param x_range: game x range
        :param y_range: game y range
        :return: in game range
        """
        return (x_range[0] <= x < x_range[1]) and (y_range[0] <= y < y_range[1])

    def check_move(self, x: int, y: int, x_range: iPair, y_range: iPair):
        """
        check if x and y are in game range
        :param x: potential x position
        :param y: potential y position
        :param x_range: game x range
        :param y_range: game y range
        :return: in game range
        """
        return self.__in_range(x, y, x_range, y_range) and self.__in_move(x, y)

    def get_moves(self, positions: set[iPair], x_range: iPair, y_range: iPair) -> list[iPair]:
        """
        returns list of possible moves
        :param positions: set of piece coordinates
        :param x_range: board width in squares
        :param y_range: board height in squares
        :return: possible moves
        """
        # positions = {piece.pos for piece in pieces}
        moves = []

        # +x
        x, y = self.pos
        x += 1
        while (pos := (x, y)) not in positions and self.check_move(x, y, x_range, y_range):
            moves.append(pos)
            x += 1

        # -x
        x, y = self.pos
        x -= 1
        while (pos := (x, y)) not in positions and self.check_move(x, y, x_range, y_range):
            moves.append(pos)
            x -= 1

        # +y
        x, y = self.pos
        y += 1
        while (pos := (x, y)) not in positions and self.check_move(x, y, x_range, y_range):
            moves.append(pos)
            y += 1

        # -y
        x, y = self.pos
        y -= 1
        while (pos := (x, y)) not in positions and self.check_move(x, y, x_range, y_range):
            moves.append(pos)
            y -= 1

        return moves

    def get_captures(self, pieces: list[Self]):
        return [pc.pos for pc in pieces if pc.color != self.color and sum(abs(self.loc - pc.loc)) == 1]

    def guess_piece(self, guess: str, other: Self) -> bool:
        """
        allows Spotter to guess rank of enemy piece
        :param guess: rank guess
        :param other: enemy piece
        :return: whether guess is correct
        """
        self.hidden = False
        if not self.rank == '1':
            return False
        if guess == other.rank:
            return True
        elif guess not in self.movement:
            print('unknown rank!!')
        return False

    def __sub__(self, other: Self) -> int:
        self.hidden = False
        other.hidden = False

        if self.rank.isdigit() and other.rank.isdigit():
            r1, r2 = int(self.rank), int(other.rank)
            if r1 > r2:
                return 1
            elif r1 < r2:
                return -1
            else:
                return 0
        elif other.rank == 'M':
            if self.rank == '3':
                return 1
            else:
                return 0
        elif other.rank == 'F':
            return 1
        elif self.rank == 'S':
            if other.rank == '10':
                return 1
            if other.rank == 'S':
                return 0
            else:
                return -1
        elif other.rank == 'S':
            return 1

        print('Case not caught!')
        print(f"{self.rank} -> {other.rank}")

    def __str__(self):
        return f"Piece('{self.rank}', {self.pos}, color='{self.color}')"

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    my_list = [
        Spy := Piece('S', (2, 2)),
        Ten := Piece('10', (1, 4)),
        Two := Piece('2', (1, 7)),
        Mine := Piece('M', (1, 1)),
        Three := Piece('3', (3, 2), 'Blue'),
    ]
