from typing import TypeAlias

iPair: TypeAlias = tuple[int, int]
sPair: TypeAlias = tuple[str, str]
Color: TypeAlias = tuple[int, int, int]

COLORS = {'red': (170, 70, 70),
          'blue': (100, 100, 160),
          'green': (20, 120, 20),
          'black': (0, 0, 0),
          'grey': (100, 100, 100),
          'cloud': (160, 160, 160),
          'white': (255, 255, 255),
          'purple': (90, 0, 140),
          'yellow': (250, 200, 0),
          'orange': (250, 110, 0)
          }

RULES = ('Tactico is a fog-of-war style turn based strategy game adapted from the popular board '
         'game Stratego. The objective of the game is to capture the flag (F). The rank of enemy '
         'pieces is concealed until they enter into combat. Higher rank pieces will win when '
         'matched against lower rank pieces. Mines (M) are unable to move or attack, but will '
         'destroy an opposing piece when attacked. The flail tank (3) can safely remove mines. '
         'The sniper (1) can remove adjacent pieces if it can correctly identify their rank. The '
         'Spy (S) can defeat the Terminator (10) if it initiates combat. Pieces may move in one '
         'direction and attack in a turn. Piece movement is based on rank. The game begins with a '
         'setup phase where both players place the pieces from the bank within the deployment '
         'zone as indicated by the yellow squares. Once all pieces have been placed, '
         'either player may choose to start the game by pressing the "esc" key. Once the game has '
         'started, pieces may move based on the rules for their rank. Legal moves are highlighted '
         'with thick yellow outline. Thin yellow outline indicates the move made on the previous '
         'turn. Following movement, you may choose to attack with the moved piece, or you may choose '
         'to end your turn using the "esc" key. Legal attacks are indicated with a white outline. '
         'When a "1" attacks, you may guess the rank of the opposing piece by selecting the '
         "corresponding tile in the opponent's piece bank. The number in the upper left corner of "
         "these tiles indicates how many are remaining on the board.")
