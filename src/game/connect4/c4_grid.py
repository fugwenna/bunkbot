from typing import List

from .c4_constants import EMPTY_PIECE, WIN_PIECE, BOARD_HEIGHT, BOARD_WIDTH
from .c4_coord import ConnectFourCoordinate
from .c4_piece import ConnectFourPiece


"""
The playing board or grid itself - basically 
a cartesian grid setup 6x7
"""
class ConnectFourGrid:
    def __init__(self):
        self.is_connect_four: bool = False
        self.pieces: List[ConnectFourPiece] = []
        self.setup()


    # on initialization, fill the grid 
    # up with a 6x7 dimenstion and automatically
    # fill empty coordinates
    def setup(self) -> None:
        for x in range(0, BOARD_WIDTH):
            for y in range(0, BOARD_HEIGHT):
                piece = ConnectFourPiece(ConnectFourCoordinate(x, y), EMPTY_PIECE)
                self.pieces.append(piece)


    def update_piece(self, col_index: int, user_id: int, color: str) -> None:
        pieces: List[ConnectFourPiece] = filter(lambda p: p.coordinate.x == col_index, self.pieces)
        s_pieces: List[ConnectFourPiece] = sorted(pieces, key=lambda x: x.coordinate.y)

        for p in s_pieces:
            if p.user_id is None:
                p.replace_with(user_id, color)
                self.check_connect_four(p)
                break


    def check_connect_four(self, p: ConnectFourPiece) -> bool:
        self.is_connect_four = True
        p.color = WIN_PIECE
