from typing import List

from .c4_constants import EMPTY_PIECE
from .c4_coord import ConnectFourCoordinate
from .c4_piece import ConnectFourPiece


"""
The playing board or grid itself - basically 
a cartesian grid setup 6x7
"""
class ConnectFourGrid:
    def __init__(self):
        self.pieces: List[ConnectFourPiece] = []
        self.setup()


    # on initialization, fill the grid 
    # up with a 6x7 dimenstion and automatically
    # fill empty coordinates
    def setup(self) -> None:
        for x in range (0, 6):
            for y in range(0, 5):
                piece = ConnectFourPiece(ConnectFourCoordinate(x, y), EMPTY_PIECE)
                self.pieces.append(piece)
