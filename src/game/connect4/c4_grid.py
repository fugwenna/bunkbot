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
                #self.check_connect_four(p)
                break


    def check_connect_four(self, piece: ConnectFourPiece) -> bool:
        player_pieces: List[ConnectFourPiece] = list(
            filter(lambda p: p.user_id == piece.user_id, self.pieces))

        win_pieces: List[ConnectFourPiece] = []
        v_pieces: List[ConnectFourPiece] = self.check_vertically(piece, player_pieces)
        h_pieces: List[ConnectFourPiece] = self.check_horizontally(piece, player_pieces)
        
        if len(v_pieces) == 3:
            win_pieces = v_pieces
        elif len(h_pieces) == 3:
            win_pieces = h_pieces

        win_pieces.extend([piece])
        for wp in win_pieces:
            wp.color = WIN_PIECE


    def check_vertically(self, piece: ConnectFourPiece, pieces: List[ConnectFourPiece]) -> None:
        connected_pieces: List[ConnectFourPiece] = []

        h_pieces: List[ConnectFourPiece] = sorted(
            filter(lambda p: p.coordinate.x == piece.coordinate.x and p.user_id == piece.user_id, self.pieces),
            key=lambda l: l.coordinate.y)

        for i in range(piece.coordinate.y, -1, -1):
            p_ref = h_pieces[i]
            if p_ref.coordinate.y == i+1:
                connected_pieces.append(p_ref)
            else:
                break

        return connected_pieces


    def check_horizontally(self, piece: ConnectFourPiece, pieces: List[ConnectFourPiece]) -> None:
        connected_pieces: List[ConnectFourPiece] = []

        v_pieces: List[ConnectFourPiece] = sorted(
            filter(lambda p: p.coordinate.y == piece.coordinate.y and p.user_id == piece.user_id, self.pieces),
            key=lambda l: l.coordinate.x)

        print(len(v_pieces))

        for i in range(piece.coordinate.x, -1, -1):
            print(i)
            p_ref = v_pieces[i]
            if p_ref.coordinate.x == i+1:
                connected_pieces.append(p_ref)
            else:
                break

        return connected_pieces
