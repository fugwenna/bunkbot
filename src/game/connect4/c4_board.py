from typing import List

from .c4_constants import BOARD_HEIGHT, BOARD_WIDTH, EMPTY_PIECE, WIN_PIECE
from .c4_piece import ConnectFourPiece


"""
The playing self.pieces or grid itself - basically 
a cartesian grid setup 6x7
"""
class ConnectFourBoard:
    def __init__(self):
        self.is_connect_four: bool = False
        self.pieces: List[List[ConnectFourPiece]] = []
        self.setup()


    # on initialization, fill the grid 
    # up with a 6x7 dimenstion and automatically
    # fill empty 
    def setup(self) -> None:
        for y in range(BOARD_HEIGHT):
            b_row: List[ConnectFourPiece] = []
            for x in range(BOARD_WIDTH):
                piece = ConnectFourPiece(x, y, EMPTY_PIECE)
                b_row.append(piece)
            self.pieces.append(b_row)


    def update_piece(self, col_index: int, user_id: int, color: str) -> None:
        pieces: List[ConnectFourPiece] = filter(lambda p: p.x == col_index, self.pieces)

        for p in pieces:
            if p.user_id is None:
                p.replace_with(user_id, color)
                #self.check_connect_four(p)
                break


    def check_connect_four(self, piece: ConnectFourPiece) -> bool:
        pass