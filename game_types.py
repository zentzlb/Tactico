from typing import TypeAlias

iPair: TypeAlias = tuple[int, int]
sPair: TypeAlias = tuple[str, str]
Color: TypeAlias = tuple[int, int, int]

COLORS = {'red': (150, 70, 70),
          'blue': (70, 70, 140),
          'green': (20, 120, 20),
          'black': (0, 0, 0),
          'grey': (100, 100, 100),
          'cloud': (160, 160, 160),
          'white': (255, 255, 255),
          'purple': (90, 0, 140),
          'yellow': (250, 200, 0),
          'orange': (250, 110, 0)
          }

RULES = ('This is a turn based strategy game with 12 unit types. The goal of the game is to capture the flag '
         '(F). Higher rank pieces will win when matched against lower rank pieces. When a piece (except a 3) attacks a '
         'mine (M) both are destroyed. ')
