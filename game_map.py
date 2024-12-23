from game_types import iPair
from pieces import Piece, Obstacle
from dataclasses import dataclass


@dataclass(frozen=True)
class Map:
    """
    game map
    """
    x_range: iPair
    y_range: iPair
    x_red_deploy: iPair
    y_red_deploy: iPair
    x_blue_deploy: iPair
    y_blue_deploy: iPair
    obstacles: set[iPair]


MAP1 = Map((0, 10), (0, 8), (0, 10), (0, 3), (0, 10), (5, 8), {(2, 3),
                                                               (2, 4),
                                                               (3, 3),
                                                               (3, 4),
                                                               (6, 3),
                                                               (6, 4),
                                                               (7, 3),
                                                               (7, 4)
                                                               })

if __name__ == '__main__':
    my_map1 = Map((1, 20), (0, 10), (1, 2), (1, 2), (1, 2), (3, 4), {(3, 4)})
    my_map2 = Map((1, 20), (0, 10), (1, 2), (3, 2), (1, 2), (3, 4), {(3, 4)})
    print(MAP1.x_range, MAP1.y_range)
