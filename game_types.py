from typing import TypeAlias

iPair: TypeAlias = tuple[int, int]
sPair: TypeAlias = tuple[str, str]
Color: TypeAlias = tuple[int, int, int]

COLORS = {'red': (180, 25, 25),
          'blue': (45, 45, 180),
          'green': (0, 200, 0),
          'black': (0, 0, 0),
          'grey': (100, 100, 100),
          'cloud': (160, 160, 160),
          'white': (255, 255, 255),
          'purple': (120, 0, 160),
          'yellow': (250, 200, 0),
          'orange': (250, 110, 0)
          }
