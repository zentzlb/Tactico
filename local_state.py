import time

import pygame
from typing import Callable
from button import Button, PieceButton, GameSquare
from game_engine import Engine
from game_map import MAP1
from game_types import iPair, sPair, Color, COLORS
from pieces import Piece
from functools import partial, partialmethod
from client import Client
from collections import defaultdict
import socket

pygame.init()


class LocalState:
    """
    game handler
    """
    colors = COLORS
    fonts = {'large': pygame.font.SysFont('Agency FB', 35),
             'medium': pygame.font.SysFont('Agency FB', 25),
             'small': pygame.font.SysFont('Agency FB', 16)}

    def __init__(self, my_engine: Engine, size: iPair, client_: Client = None):

        self.run = True
        self.size = size
        self.engine = my_engine
        self.game_mode = 'main_menu'
        self.modes = {'main_menu', 'single_player', 'waiting', 'Red', 'Blue'}
        self.main_menu = {'Single Player': partial(self.set_mode, 'single_player'),
                          'Multiplayer': lambda *args, **kwargs: self.connect(),
                          'Quit': lambda *args, **kwargs: self.quit()}
        self.window = pygame.display.set_mode(size)
        self.background = pygame.Surface(self.size)
        self.buttons: dict[tuple, Button | PieceButton] = {}
        self.squares_dict: dict[tuple, GameSquare] = self.game_squares
        self.selected: iPair | sPair | tuple = tuple()
        self.guess_target: iPair | sPair | tuple = tuple()
        self.client = client_
        self.make_background()

    @property
    def team(self) -> str:
        """
        local player team color -> 'Red' or 'Blue'
        """
        match self.game_mode:
            case 'main_menu':
                return ''
            case 'single_player':
                return self.engine.turn
            case _:
                return self.game_mode

    @property
    def opponent(self) -> str:
        """
        opponent team color -> 'Red' or 'Blue'
        """
        if (team := self.team) == 'Red':
            return 'Blue'
        elif team == 'Blue':
            return 'Red'
        return 'no opponent'

    @property
    def moves(self) -> list[iPair]:
        """
        gets list of moves from selected piece
        """
        if self.selected in self.buttons and not self.engine.move:
            if type(button := self.buttons[self.selected]) is PieceButton and not self.engine.setup:
                positions = {*{piece.pos for piece in self.engine.pieces}, *self.engine.map.obstacles}
                return button.piece.get_moves(positions,
                                              self.engine.map.x_range,
                                              self.engine.map.y_range)

            elif self.engine.setup:

                if type(self.selected[0]) is str:
                    if not self.engine.piece_bank[self.team][self.selected[1]] > 0:
                        return []

                return [pos for i in self.engine.deploy_range(self.team, 'x')
                        for j in self.engine.deploy_range(self.team, 'y')
                        if (pos := (i, j)) not in self.engine.map.obstacles
                        and pos != self.selected]

        return []

    @property
    def captures(self) -> list[iPair]:
        """
        gets list of captures from selected piece
        NEED TO REFERENCE ENGINE.MOVE
        """
        if self.is_piece:
            return self.piece.get_captures(self.engine.pieces)
        return []

    @property
    def length(self) -> float:
        """
        game box length
        """
        width, height = self.size
        dw = width / max((self.game_w + 1, len(self.engine.total_pieces.keys()) + 1))
        dh = height / (self.game_h + 4)
        return min((dw, dh))

    @property
    def square_size(self) -> float:
        """
        size of game squares
        """
        return self.length * 0.9

    @property
    def game_w(self) -> int:
        """
        game width in terms of game squares
        """
        return self.engine.map.x_range[1] - self.engine.map.x_range[0]

    @property
    def game_h(self) -> int:
        """
        game height in terms of game squares
        """
        return self.engine.map.y_range[1] - self.engine.map.y_range[0]

    @property
    def is_piece(self) -> bool:
        """
        determines if current selection is a piece
        """
        return self.selected and type(self.piece) is Piece

    @property
    def piece(self) -> Piece:
        """
        selected piece
        """
        return self.engine[self.selected]

    @property
    def game_squares(self) -> dict[tuple, GameSquare]:
        """
        dictionary of game squares
        """

        def ind(color: str) -> int:
            if color == 'Red':
                return self.game_h + 1
            else:
                return self.game_h + 2

        size = self.square_size
        board_squares: dict[tuple, GameSquare] = {
            (i, j): GameSquare(self.i2x(i, size), self.i2x(j, size), size, size, (i, j))
            for i in range(self.game_w) for j in range(self.game_h)}

        bank_squares: dict[tuple, GameSquare] = {
            (color, rank):
                GameSquare(self.i2x(i, size), self.i2x(ind(color), size), size,
                           size, (color, rank))
            for color in self.engine.piece_bank
            for i, rank in enumerate(self.engine.piece_bank[color])}

        return board_squares | bank_squares

    def connect(self):
        if type(self.client) is Client:
            self.client.close()
        self.client = Client(socket.gethostbyname('DEEP-BLUE'), 5555, up=self.update, end=self.end)
        self.client.start_thread()
        time.sleep(0.1)
        if self.set_mode(self.client.team):
            self.update()
            return True
        self.set_mode('main_menu')
        return False

    def update(self):
        """
        updates game data from Client connection
        """
        print('updating')
        if self.client and type(self.client.data) is dict:
            self.engine.data = self.client.data
            if self.engine.game_over:
                self.set_mode('waiting')
            self.make_buttons()

    def end(self):
        """
        handles Client connection loss
        """
        if self.client:
            self.client.close()
            self.client = None
        self.set_mode('main_menu')

    def quit(self):
        """
        ends game
        """
        pygame.quit()
        self.run = False

    def set_mode(self, mode: str, *args, **kwargs) -> bool:
        """
        set game mode and check if valid
        :param mode: mode to change to
        :param args:
        :param kwargs:
        """
        print(mode)
        if mode in self.modes:
            if self.game_mode == 'waiting' and mode == 'main_menu':
                self.engine.restart()
            self.game_mode = mode
            self.make_background()
            self.make_buttons()
            return True
        print(f"{mode} is not a recognized mode")
        return False

    def piece_fn(self, button: PieceButton | None = None):
        """
        select or deselect piece
        :param button: piece button
        """
        if self.selected == button.piece.pos or (not self.engine.setup and button.piece.rank in ('F', 'M')):
            self.selected = tuple()
        elif button.piece.color == self.engine.turn or (self.engine.setup and button.piece.color == self.team):
            self.selected = button.piece.pos
        self.make_buttons()

    def bank_fn(self, team: str, button: Button | None = None):
        """
        select or deselect bank button
        :param team: team color -> 'Red' or 'Blue'
        :param button: bank button
        """
        pos = (team, button.text)

        if self.selected == pos:
            self.selected = tuple()
        else:
            self.selected = pos
        self.make_buttons()

    def wait_buttons(self):
        """
        make await action buttons
        """
        y = self.window.get_height() - self.fonts['large'].get_height() - 20
        h = self.fonts['large'].get_height() + 10

        if self.engine.game_over:
            text = 'main menu'
            mode = 'main_menu'
            color = self.colors['green']
        else:
            text = 'begin turn'
            mode = 'single_player'
            color = self.colors[self.engine.turn.lower()]

        start_button = Button((10, y, 150, h),
                              self.fonts,
                              text=text,
                              color=color,
                              func=lambda *args, **kwargs: self.set_mode(mode))
        other_buttons = {(team, rank):
                             Button(self.squares_dict[(team, rank)].rect,
                                    self.fonts,
                                    text=rank,
                                    color=self.colors[team.lower()],
                                    subtext=str(self.engine.piece_count[team][rank]))
                         for team in self.engine.piece_bank
                         for rank in self.engine.piece_bank[team]}
        self.buttons = {(0, 0): start_button} | other_buttons
        return

    def menu_buttons(self):
        """
        make main menu buttons
        """
        x_start = 100
        y_start = 100
        height = self.fonts['large'].get_height() + 20
        width = 200

        self.buttons = {(0, i): Button((x_start,
                                        y_start + i * (height + 20),
                                        width,
                                        height),
                                       self.fonts,
                                       text=option,
                                       color=self.colors['red'],
                                       text_color=self.colors['blue'],
                                       func=self.main_menu[option])
                        for i, option in enumerate(self.main_menu)}

    def game_buttons(self) -> None:
        """
        make game buttons
        """

        piece_buttons = {pc.pos: PieceButton(self.squares_dict[pc.pos].rect,
                                             pc,
                                             self.colors['black'],
                                             self.fonts,
                                             func=self.piece_fn)
                         for pc in self.engine.pieces
                         if pc.color == self.team}

        move_buttons = {move:
                            Button(self.game_squares[move].rect,
                                   self.fonts,
                                   color=self.colors['yellow'],
                                   rect_width=3,
                                   func=partial(self.submit_move, self.selected, move))
                        for move in self.moves}

        if not self.engine.setup and self.is_piece:
            print(self.guess_target)
            if self.guess_target:
                guesses = {(team := self.opponent, rank):
                               Button(self.game_squares[(team, rank)].rect,
                                      self.fonts,
                                      text=rank,
                                      color=self.colors[team.lower()],
                                      subtext=str(self.engine.piece_count[team][rank]),
                                      func=partial(self.submit_guess,
                                                   self.selected,
                                                   self.guess_target,
                                                   rank))
                           for rank in self.engine.piece_bank[self.opponent]}
                capture = {self.guess_target:
                               Button(self.game_squares[self.guess_target].rect,
                                      self.fonts,
                                      color=self.colors['white'],
                                      rect_width=4,
                                      func=partial(self.submit_capture, self.selected, self.guess_target))}
                cap_buttons = guesses | capture

            elif self.piece.rank == '1':
                cap_buttons = {capture:
                                   Button(self.game_squares[capture].rect,
                                          self.fonts,
                                          color=self.colors['orange'],
                                          rect_width=5,
                                          func=partial(self.init_guess, capture))
                               for capture in self.captures}

            else:
                cap_buttons = {capture:
                                   Button(self.game_squares[capture].rect,
                                          self.fonts,
                                          color=self.colors['white'],
                                          rect_width=5,
                                          func=partial(self.submit_capture, self.selected, capture))
                               for capture in self.captures}

        else:
            cap_buttons = {}
        if self.engine.setup:
            other_buttons = {(team := self.team, rank):
                                 Button(self.squares_dict[(team, rank)].rect,
                                        self.fonts,
                                        text=rank,
                                        color=self.colors[team.lower()],
                                        subtext=str(self.engine.piece_bank[team][rank]),
                                        func=partial(self.bank_fn, team))
                             for rank in self.engine.piece_bank[self.team]}

        elif not self.guess_target:
            other_buttons = {(team, rank):
                                 Button(self.squares_dict[(team, rank)].rect,
                                        self.fonts,
                                        text=rank,
                                        color=self.colors[team.lower()],
                                        subtext=str(self.engine.piece_count[team][rank]))
                             for team in self.engine.piece_bank
                             for rank in self.engine.piece_bank[team]}

        else:
            other_buttons = {}
            self.guess_target = tuple()
        print(cap_buttons)
        self.buttons = piece_buttons | move_buttons | cap_buttons | other_buttons

    def make_buttons(self):
        """
        makes buttons based on game mode
        """
        match self.game_mode:
            case 'main_menu':
                self.menu_buttons()
            case 'single_player':
                self.game_buttons()
            case 'waiting':
                self.wait_buttons()
            case _:
                self.game_buttons()

    def i2x(self, index: int, size: float) -> float:
        """
        maps game map index to pixel position
        :param index: map index
        :param size: window size
        :return: pixel position
        """
        return (index + 1) * self.length - size // 2

    def make_background(self):
        """
        updates game background
        :return:
        """
        self.background.fill(self.colors['black'])
        if self.game_mode != 'main_menu':
            rect_width = 3
            for square in self.squares_dict.values():
                pygame.draw.rect(self.background, self.colors['cloud'], square.rect)

    def submit(self, method: str, *args) -> bool:
        """
        handles submissions based on game mode
        :param method: type of submission: make_move, make_capture, make_guess
        :param args: submission arguments
        :return: submission success
        """
        print()
        print(f"{method=}")
        print(f"{args=}")
        print()
        if self.game_mode == "single_player":
            return self.engine.__getattribute__(method)(*args)
        if self.client:
            return self.client.transmit((method, *args))
        return False
        # return sp

    def submit_move(self, old_pos: iPair, new_pos: iPair, **kwargs):
        """
        move piece to new position
        :param old_pos: old position
        :param new_pos: new position
        :return:
        """
        print('submitted')
        # if self.engine.make_move(old_pos, new_pos):
        if self.submit('make_move', old_pos, new_pos):
            self.selected = new_pos
            # if not self.captures and not self.engine.setup:
            #     self.end_turn()
            # else:
            #     del self.buttons[new_pos]
        self.make_buttons()

    def submit_capture(self, pos: iPair, capture: iPair, **kwargs):
        """
        capture enemy piece
        :param pos: current position
        :param capture: capture position
        :return:
        """
        # if self.engine.make_capture(pos, capture):
        if self.submit('make_capture', pos, capture):
            self.selected = tuple()
            if self.game_mode == 'single_player' or self.engine.game_over:
                self.set_mode('waiting')
            self.make_buttons()

    def submit_guess(self, pos: iPair, capture: iPair, guess: str, **kwargs):
        """
        guess enemy piece rank
        :param pos: current position
        :param capture: capture position
        :param guess: rank guess
        """
        # if self.engine.make_guess(pos, capture, guess):
        if self.submit('make_guess', pos, capture, guess):
            self.selected = tuple()
            self.make_buttons()
            if self.game_mode == 'single_player':
                self.set_mode('waiting')

    def end_turn(self):
        if self.submit('new_turn'):
            if self.game_mode == 'waiting':
                return
            if self.game_mode == 'single_player':
                self.set_mode('waiting')

            self.selected = tuple()
            self.make_buttons()

    def init_guess(self, capture: iPair, **kwargs):
        """
        initialize guessing
        :param capture: capture position
        """
        self.guess_target = capture
        self.make_buttons()

    def draw_piece(self, piece: Piece):
        """
        draws game piece onto game window
        :param piece: game piece
        :return:
        """
        size = self.length * 0.9
        i, j = piece.pos
        rect = pygame.Rect(self.i2x(i, size), self.i2x(j, size), size, size)
        pygame.draw.rect(self.window, self.colors[piece.color.lower()], rect)
        if not piece.hidden or self.team == piece.color:
            text_surface = self.fonts['large'].render(piece.rank,
                                                      True,
                                                      self.colors['black'])
            xt = rect.centerx - text_surface.get_width() / 2
            yt = rect.centery - text_surface.get_height() / 2
            self.window.blit(text_surface, (xt, yt))

    def draw_rect(self, rect: pygame.Rect, color: str, text: str = '', width: int = 0):
        pygame.draw.rect(self.window,
                         self.colors[color],
                         rect,
                         width=width)

        text_surface = self.fonts['medium'].render(text,
                                                   True,
                                                   self.colors['yellow'])
        xt = rect.centerx - text_surface.get_width() / 2
        yt = rect.centery - text_surface.get_height() / 2
        self.window.blit(text_surface, (xt, yt))

    def draw(self):

        self.window.blit(self.background, (0, 0))

        # Rectangle Dimensions
        size = self.length * 0.9
        rect_width = 3

        if self.game_mode != 'main_menu':

            for obs in self.engine.map.obstacles:
                i, j = obs
                pygame.draw.rect(self.window, self.colors['black'],
                                 (self.i2x(i, size), self.i2x(j, size), size, size))

            for pc in self.engine.pieces:
                if (pc.color != engine.turn or self.engine.setup or self.game_mode == 'waiting' or
                        (self.game_mode in ('Red', 'Blue') and pc.color != self.game_mode)):
                    self.draw_piece(pc)

        for button in self.buttons.values():
            button.draw(self.window)

        if self.engine.moves and self.game_mode != 'main_menu':
            if move := self.engine.moves[-1]['move'] or self.engine.moves[-min(2, len(self.engine.moves))]['move']:
                old_pos, new_pos = move
                pygame.draw.rect(self.window,
                                 self.colors['yellow'],
                                 self.game_squares[old_pos].rect,
                                 width=2)
                pygame.draw.rect(self.window,
                                 self.colors['yellow'],
                                 self.game_squares[new_pos].rect,
                                 width=2)
            if len(self.engine.moves) >= 2:
                if capture := self.engine.moves[-2]['capture']:
                    pos, cap, losers = capture
                    pygame.draw.rect(self.window,
                                     self.colors['white'],
                                     self.game_squares[cap].rect,
                                     width=2)
                    for loser in losers:
                        pygame.draw.rect(self.window,
                                         self.colors['white'],
                                         self.game_squares[loser].rect,
                                         width=2)
                if capture := self.engine.moves[-2]['guess']:
                    pos, cap, guess = capture
                    pygame.draw.rect(self.window,
                                     self.colors['orange'],
                                     self.game_squares[cap].rect,
                                     width=2)
                    pygame.draw.rect(self.window,
                                     self.colors['orange'],
                                     self.game_squares[(self.engine.moves[-1]['turn'], guess)].rect,
                                     width=2)

        if self.selected:
            pygame.draw.rect(self.window,
                             self.colors['green'],
                             self.game_squares[self.selected].rect,
                             width=3)

        self.draw_rect(pygame.Rect(self.size[0] - 120, 0, 120, 50), self.engine.turn.lower(), self.game_mode)

        pygame.display.update()

    def game_loop(self):
        """
        game loop requiring a game engine
        """

        clock = pygame.time.Clock()
        fps = 60

        self.make_buttons()

        while self.run:
            clock.tick(fps)

            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # quit if user quits
                    self.run = False
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    buttons = [button for button in self.buttons.values() if button.collidepoint(pos)]
                    for button in buttons:
                        button()

                elif event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_ESCAPE]:
                        self.end_turn()
                        print('new turn')


if __name__ == '__main__':
    engine = Engine(MAP1)

    engine.pieces = [Piece('7', (1, 2), color='Red'),
                     Piece('3', (4, 2), color='Red'),
                     Piece('10', (9, 5), color='Blue'),
                     Piece('M', (3, 7), color='Blue'),
                     Piece('6', (2, 2), color='Red'),
                     Piece('9', (2, 1), color='Red'),
                     Piece('10', (3, 1), color='Red'),
                     Piece('4', (5, 1), color='Red'),
                     Piece('S', (8, 2), color='Red'),
                     Piece('1', (9, 2), color='Red'),
                     Piece('2', (5, 2), color='Red'),
                     Piece('2', (7, 2), color='Red'),
                     Piece('2', (7, 1), color='Red'),
                     Piece('2', (6, 1), color='Red'),
                     Piece('1', (0, 2), color='Red'),
                     Piece('M', (9, 0), color='Red'),
                     Piece('M', (3, 2), color='Red'),
                     Piece('M', (8, 0), color='Red'),
                     Piece('M', (7, 0), color='Red'),
                     Piece('M', (6, 0), color='Red'),
                     Piece('F', (0, 0), color='Red'),
                     Piece('3', (1, 1), color='Red'),
                     Piece('3', (0, 1), color='Red'),
                     Piece('2', (4, 1), color='Red'),
                     Piece('2', (6, 2), color='Red'),
                     Piece('3', (8, 1), color='Red'),
                     Piece('3', (9, 1), color='Red'),
                     Piece('4', (5, 0), color='Red'),
                     Piece('5', (4, 0), color='Red'),
                     Piece('5', (3, 0), color='Red'),
                     Piece('6', (2, 0), color='Red'),
                     Piece('8', (1, 0), color='Red'),
                     Piece('1', (8, 5), color='Blue'),
                     Piece('1', (0, 5), color='Blue'),
                     Piece('S', (1, 5), color='Blue'),
                     Piece('M', (9, 6), color='Blue'),
                     Piece('M', (8, 7), color='Blue'),
                     Piece('F', (9, 7), color='Blue'),
                     Piece('7', (5, 5), color='Blue'),
                     Piece('6', (4, 5), color='Blue'),
                     Piece('6', (3, 5), color='Blue'),
                     Piece('5', (2, 5), color='Blue'),
                     Piece('5', (6, 5), color='Blue'),
                     Piece('4', (7, 5), color='Blue'),
                     Piece('3', (7, 6), color='Blue'),
                     Piece('3', (8, 6), color='Blue'),
                     Piece('3', (7, 7), color='Blue'),
                     Piece('3', (6, 6), color='Blue'),
                     Piece('3', (6, 7), color='Blue'),
                     Piece('2', (5, 6), color='Blue'),
                     Piece('2', (5, 7), color='Blue'),
                     Piece('2', (4, 6), color='Blue'),
                     Piece('2', (4, 7), color='Blue'),
                     Piece('2', (3, 6), color='Blue'),
                     Piece('4', (2, 6), color='Blue'),
                     Piece('2', (1, 6), color='Blue'),
                     Piece('8', (0, 6), color='Blue'),
                     Piece('9', (0, 7), color='Blue'),
                     Piece('M', (1, 7), color='Blue'),
                     Piece('M', (2, 7), color='Blue')]
    ls = LocalState(engine, (700, 700))
    ls.game_loop()
