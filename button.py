import pygame
from pieces import Piece
from game_types import iPair, Color, COLORS
from dataclasses import dataclass
from typing import Callable


class Button(pygame.FRect):
    """
    generic button
    """
    colors = COLORS

    def __init__(self,
                 rect: tuple[float, float, float, float],
                 fonts: dict[str, pygame.font.Font],
                 text: str = '',
                 subtext: str = '',
                 rect_width: int = 0,
                 text_color: Color = (0, 0, 0),
                 color: Color = (100, 100, 100),
                 func: Callable = lambda *args, **kwargs: None):
        super().__init__(rect)
        self.__color = color
        self.rect_width = rect_width
        self.text_color = text_color
        self.text = text
        self.subtext = subtext
        self.fonts = fonts
        self.func = func

    @property
    def color(self) -> Color:
        """
        button color
        :return:
        """
        return self.__color

    def draw(self, surf: pygame.Surface) -> None:
        """
        draw_game button on a surface
        :param surf: surface
        :return:
        """
        pygame.draw.rect(surf, self.color, self, width=self.rect_width)
        self.draw_text(surf)
        self.draw_subtext(surf)

    def draw_text(self, surf: pygame.Surface) -> None:
        """
        blits text onto surface centered on centerx, centery
        :param surf: surface to blit onto
        :return:
        """
        # if self.text_color != (0, 0, 0):
        #     print(self.text_color)
        if self.text:
            text_surface = self.fonts['large'].render(self.text,
                                                      True,
                                                      self.text_color)
            xt = self.centerx - text_surface.get_width() / 2
            yt = self.centery - text_surface.get_height() / 2
            surf.blit(text_surface, (xt, yt))

    def draw_subtext(self, surf: pygame.Surface) -> None:
        """
        blits text onto surface centered on x, y
        :param surf: surface to blit onto
        :return:
        """
        if self.subtext:
            text_surface = self.fonts['small'].render(self.subtext,
                                                      True,
                                                      self.text_color)
            xt = self.x + 3
            yt = self.y + 3
            surf.blit(text_surface, (xt, yt))

    def __call__(self, *args, **kwargs):
        kwargs['button'] = self
        return self.func(*args, **kwargs)

    def __str__(self):
        return f"Button: {self.color} |  {self.text} | {self.subtext}"

    def __repr__(self):
        return self.__str__()


class PieceButton(Button):
    """
    rectangle object to represent game piece
    """

    # colors = {'Red': (200, 0, 0), 'Blue': (0, 0, 200)}

    def __init__(self,
                 rect: tuple[float, float, float, float],
                 piece: Piece,
                 text_color: Color,
                 fonts: dict[str, pygame.font.Font],
                 rect_width: int = 0,
                 func: Callable = lambda: None):
        super().__init__(rect,
                         fonts,
                         text=piece.rank,
                         text_color=text_color,
                         rect_width=rect_width,
                         func=func)
        self.piece = piece

    @property
    def color(self) -> Color:
        return self.colors[self.piece.color.lower()]

    def __str__(self):
        return f"Piece Button: {self.color} |  {self.text} | {self.subtext}"


@dataclass
class GameSquare:
    """
    provides mapping between game significant data and screen location
    """
    x: float
    y: float
    w: float
    h: float
    name: tuple

    @property
    def rect(self) -> tuple[float, float, float, float]:
        """
        pygame rectangle representation
        :return:
        """
        return self.x, self.y, self.w, self.h

    @rect.setter
    def rect(self, value: tuple):
        self.x, self.y, self.w, self.h = value



