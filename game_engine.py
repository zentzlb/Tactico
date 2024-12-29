from game_types import iPair, sPair
from pieces import Piece
from game_map import Map, MAP1
from typing import Callable
from functools import wraps
from copy import deepcopy
import pickle

STRENGTH = {
    '10': 10,
    '9': 9,
    '8': 8,
    '7': 8,
    '6': 7,
    '5': 5,
    '4': 4,
    '3': 5,
    '2': 4,
    '1': 8,
    'S': 3,
    'M': 2,
    'F': 0,
}


class Engine:
    """
    handles Tactico game logic
    """

    total_pieces = {
        '10': 1,
        '9': 1,
        '8': 1,
        '7': 1,
        '6': 2,
        '5': 2,
        '4': 2,
        '3': 5,
        '2': 6,
        '1': 2,
        'S': 1,
        'M': 5,
        'F': 1,
    }

    def __init__(self, my_map: Map):
        """
        :param my_map: game map
        """
        self.map = my_map
        self.color_map = {1: 'Red', -1: 'Blue'}
        self._turn_sign = 1
        self.move: iPair | tuple = tuple()
        self.history: list[dict] = []
        self.pieces: list[Piece] = []
        self.setup = True
        self.game_over = False
        self.index = 0
        # self.moved_piece: Pair | tuple = tuple()

    def deploy_range(self, team: str, dim: str = 'x') -> range:
        """
        gets deployment range
        :param team: team color -> 'Red' or 'Blue'
        :param dim: 'x' or 'y'
        :return: deployment range
        """
        return range(*self.map.__getattribute__(f'{dim}_{team.lower()}_deploy'))

    @property
    def position(self):
        if self.game_over:
            return self.history[self.index]['position']
        return self.pieces

    @property
    def i(self):
        if self.game_over:
            return self.index
        return len(self.history) - 1

    @property
    def move_dict(self):
        return {'position': deepcopy(self.pieces),
                'turn': self.turn,
                'move': tuple(),
                'capture': tuple(),
                'guess': tuple()}

    @property
    def data(self) -> dict:
        """
        relevant game data in dictionary form
        """
        return self.__dict__

    @data.setter
    def data(self, value: dict):
        self.__dict__ = value

    @property
    def piece_bank(self) -> dict[str, [dict[str, [int]]]]:
        """
        pieces remaining in the bank
        """
        return {'Red': {rank: self.total_pieces[rank] - self.count_pieces('Red', rank)
                        for rank in self.total_pieces},
                'Blue': {rank: self.total_pieces[rank] - self.count_pieces('Blue', rank)
                         for rank in self.total_pieces}}

    @property
    def strength(self) -> dict[str, float]:
        return {'Red': sum([STRENGTH[piece.rank] if piece.hidden else STRENGTH[piece.rank] / 2
                            for piece in self.pieces if piece.color == 'Red']),
                'Blue': sum([STRENGTH[piece.rank] if piece.hidden else STRENGTH[piece.rank] / 2
                            for piece in self.pieces if piece.color == 'Blue'])
                }

    @property
    def piece_count(self) -> dict[str, [dict[str, [int]]]]:
        """
        remaining pieces by color and rank on the board
        """
        return {'Red': {rank: self.count_pieces('Red', rank)
                        for rank in self.total_pieces},
                'Blue': {rank: self.count_pieces('Blue', rank)
                         for rank in self.total_pieces}}

    @property
    def turn(self) -> str:
        """
        gives the color of whose turn it is -> 'Red' or 'Blue'
        """
        if self.game_over:
            return self.history[self.index]['turn']
        return self.color_map[self._turn_sign]

    @property
    def piece_dict(self) -> dict[iPair, Piece]:
        """
        dictionary of pieces by their position coordinates
        """
        return {piece.pos: piece for piece in self.pieces}

    @property
    def positions(self) -> set[iPair]:
        """
        set of piece and obstacle position coordinates
        """
        return {*{piece.pos for piece in self.pieces}, *self.map.obstacles}

    def __in_game(fn: Callable, *garbage) -> Callable:
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            if self.game_over:
                return False
            else:
                return fn(self, *args, **kwargs)

        return wrapper

    def __getitem__(self, item):
        try:
            return self.piece_bank[item[0]][item[1]]
        except KeyError:
            try:
                return self.piece_dict[item]
            except KeyError:
                print('item not found')
                return False

    def resend(self):
        pass

    def inc_up(self):
        if self.index < len(self.history) - 1:
            self.index += 1

    def inc_down(self):
        if self.index > 0:
            self.index -= 1

    def restart(self):
        """
        restarts game
        """
        self.setup = True
        self.game_over = False
        self.pieces = []
        self.history = []
        self.index = 0
        self._turn_sign = 1

    def count_pieces(self, color: str, rank: str) -> int:
        """
        counts number of pieces in play
        :param color: team color ('Red' or 'Blue')
        :param rank: piece rank
        :return: count
        """
        return len([piece for piece in self.pieces
                    if piece.rank == rank and piece.color == color])

    @__in_game
    def new_turn(self):
        if self.history:
            self.history[-1]['position'] = deepcopy(self.pieces)
        if self.game_over:
            self.restart()
        self._turn_sign *= -1
        self.move = tuple()
        if self.setup and sum(self.piece_bank['Red'].values()) + sum(self.piece_bank['Blue'].values()) == 0:
            self.setup = False
            self._turn_sign = 1
        if not self.setup:
            self.history.append(self.move_dict)
        print(f"it is now {self.turn}'s turn")
        return True

    def check_move(self, old_pos: iPair | sPair, new_pos: iPair) -> bool:
        """
        check if move is legal
        :param old_pos: the original piece location
        :param new_pos: new location
        :return: if move is legal
        """
        if self.move:
            return False

        pieces = self.piece_dict
        if old_pos in pieces:
            # positions = {*{piece for piece in pieces}, *self.map.obstacles}
            piece = pieces[old_pos]
            if piece.color != self.turn and not self.setup:
                return False
            moves = piece.get_moves(self.positions, self.map.x_range, self.map.y_range)
            if new_pos in moves:
                return True
            else:
                return False
        else:
            return False

    def check_deployment(self, team: str, pos: iPair) -> bool:
        """
        checks if deployment square is legal
        :param team: team color -> 'Red' or 'Blue'
        :param pos: game position
        :return: whether deployment is legal
        """
        if pos in self.map.obstacles:
            return False
        if pos[0] in self.deploy_range(team, 'x') and pos[1] in self.deploy_range(team, 'y'):
            return True
        return False

    @__in_game
    def make_move(self, old_pos: sPair | iPair, new_pos: iPair) -> bool:
        """
        makes move if legal
        :param old_pos: the original piece location
        :param new_pos: new location
        :return: move is legal
        """
        if self.setup:
            if not type(team := old_pos[0]) is str:
                team = self.piece_dict[old_pos].color
            if self.check_deployment(team, new_pos):
                self.place_piece(old_pos, new_pos)
                return True
            return False

        elif self.check_move(old_pos, new_pos):
            self.place_piece(old_pos, new_pos)
            self.move = new_pos
            # self.history[-1]['position'] = deepcopy(self.pieces)
            self.history[-1]['move'] = (old_pos, new_pos)
            return True
        return False

    @__in_game
    def place_piece(self, old_pos: sPair | iPair, new_pos: iPair):
        if (team := old_pos[0]) in (bank := self.piece_bank):
            if bank[team][rank := old_pos[1]] > 0:
                if new_pos in (dic := self.piece_dict):
                    self.pieces.remove(dic[new_pos])
                self.pieces.append(Piece(rank, new_pos, team))
                return True
            return False
        if new_pos in (dic := self.piece_dict):
            dic[old_pos].pos, dic[new_pos].pos = new_pos, old_pos
        else:
            dic[old_pos].pos = new_pos
        return True

    @__in_game
    def make_guess(self, pos: iPair | tuple, capture: iPair, guess: str) -> bool:
        """
        attempts to guess enemy rank
        :param pos: piece position
        :param capture: capture location
        :param guess: opponent rank guess
        :return: capture move is legal
        """
        if not pos:
            return False
        piece = self.piece_dict[pos]
        if piece.rank != '1':
            return False
        if capture in piece.get_captures(self.pieces):
            enemy = self.piece_dict[capture]
            if piece.guess_piece(guess, enemy):
                if enemy.rank == 'F':
                    self.game_over = True
                    self.index = len(self.history) - 1
                    for piece in self.pieces:
                        piece.hidden = False
                    return True
                self.pieces = [pc for pc in self.pieces if pc.pos != enemy.pos]
                self.history[-1]['guess'] = (pos, capture, guess)
                # self.history[-1]['position'] = deepcopy(self.pieces)
            else:
                print(f'{guess} was an incorrect guess')
            self.new_turn()
            return True
        return False

    @__in_game
    def make_capture(self, pos: iPair | tuple, capture: iPair) -> bool:
        """
        attempts to capture piece
        :param pos: piece position
        :param capture: capture location
        :return: capture move is legal
        """
        if not pos:
            return False
        piece = self.piece_dict[pos]
        if capture in piece.get_captures(self.pieces):
            enemy = self.piece_dict[capture]
            if enemy.rank == 'F':
                self.history[-1]['capture'] = (pos, capture, ((enemy.color, enemy.rank),))
                self.history[-1]['position'] = deepcopy(self.pieces)
                self.game_over = True
                self.index = len(self.history) - 1
                for piece in self.pieces:
                    piece.hidden = False
                return True
            winner = piece - enemy
            if winner == 1:
                self.pieces = [pc for pc in self.pieces if pc.pos != enemy.pos]
                self.history[-1]['capture'] = (pos, capture, ((enemy.color, enemy.rank),))
                piece.pos = enemy.pos
                print('win')
            elif winner == -1:
                self.pieces = [pc for pc in self.pieces if pc.pos != piece.pos]
                self.history[-1]['capture'] = (pos, capture, ((piece.color, piece.rank),))
                print('lose')
            elif winner == 0:
                self.pieces = [pc for pc in self.pieces if pc.pos not in {piece.pos, enemy.pos}]
                self.history[-1]['capture'] = (pos, capture, ((piece.color, piece.rank), (enemy.color, enemy.rank)))
                print('tie')
            # self.history[-1]['position'] = deepcopy(self.pieces)
            self.new_turn()
            return True
        return False


if __name__ == '__main__':
    eng = Engine(MAP1)
    print(eng.data)
    pass
