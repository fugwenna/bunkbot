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
        self.play_count: int = 0
        self.last_drop_location: str = None
        self.setup()


    # on initialization, fill the grid 
    # up with a 6x7 dimenstion and automatically
    # fill empty 
    def setup(self) -> None:
        for x in range(BOARD_WIDTH):
            b_col: List[ConnectFourPiece] = []
            for y in range(BOARD_HEIGHT):
                piece = ConnectFourPiece(x, y, EMPTY_PIECE)
                b_col.append(piece)
            self.pieces.append(b_col)


    def update_piece(self, col_index: int, user_id: int, color: str) -> bool:
        was_updated: bool = False
        pieces: List[ConnectFourPiece] = self.pieces[col_index]

        for p in pieces:
            if p.user_id is None:
                self.last_drop_location = "{0} (row {1})".format(p.x+1, p.y+1)
                p.replace_with(user_id, color)
                self.check_connect_four(p)
                self.play_count += 1
                was_updated = True
                break

        return was_updated


    def check_connect_four(self, piece: ConnectFourPiece) -> None:
        v_pieces: List[ConnectFourPiece] = self.get_vertical_pieces(piece)
        if len(v_pieces) == 4:
            self.create_connect_four(v_pieces)
            return

        flat_pieces: List[ConnectFourPiece] = [item for fl in self.pieces for item in fl]
        h_pieces: List[ConnectFourPiece] = self.get_horizontal_pieces(piece, flat_pieces)
        if len(h_pieces) == 4:
            self.create_connect_four(h_pieces)
            return

        d_pieces: List[ConnectFourPiece] = self.get_diagonal_pieces(piece, flat_pieces)
        if len(d_pieces) == 4:
            self.create_connect_four(d_pieces)


    def get_vertical_pieces(self, piece: ConnectFourPiece) -> List[ConnectFourPiece]:
        anchors: List[ConnectFourPiece] = self.pieces[piece.x]
        return self.loop_and_get_pieces(piece.user_id, anchors, piece.y, -1, -1)


    def get_horizontal_pieces(self, piece: ConnectFourPiece, flat_pieces: List[ConnectFourPiece]) -> List[ConnectFourPiece]:
        anchors: List[ConnectFourPiece] = sorted(list(filter(lambda p: p.y == piece.y, flat_pieces)), key=lambda s: s.x)
        hpl: List[ConnectFourPiece] = self.loop_and_get_pieces(piece.user_id, anchors, piece.x, -1, -1)
        hpr: List[ConnectFourPiece] = self.loop_and_get_pieces(piece.user_id, anchors, piece.x, BOARD_WIDTH, 1)
        return set(hpl+hpr)

    
    def get_diagonal_pieces(self, piece: ConnectFourPiece, flat_pieces: List[ConnectFourPiece]) -> List[ConnectFourPiece]:
        ru_pieces: List[ConnectFourPiece] = self.loop_and_get_pieces_d(piece, 1, 1)
        rd_pieces: List[ConnectFourPiece] = self.loop_and_get_pieces_d(piece, 1, -1)
        ld_pieces: List[ConnectFourPiece] = self.loop_and_get_pieces_d(piece, -1, -1)
        lu_pieces: List[ConnectFourPiece] = self.loop_and_get_pieces_d(piece, -1, 1)
        return max([set(ld_pieces+ru_pieces), set(lu_pieces+rd_pieces)], key=len)
        

    def loop_and_get_pieces(self, user_id: int, anchors: List[ConnectFourPiece], start: int, stop: int, direction: int) -> List[ConnectFourPiece]:
        pieces: List[ConnectFourPiece] = []

        for i in range(start, stop, direction):
            piece: ConnectFourPiece = anchors[i]

            if piece.user_id == user_id:
                pieces.append(piece)
            else:
                break

            if len(pieces) == 4:
                return pieces

        return pieces


    def loop_and_get_pieces_d(self, piece: ConnectFourPiece, x_dir: int, y_dir: int) -> List[ConnectFourPiece]:
        x_offset: int = piece.x
        y_offset: int = piece.y
        x_stop: int = (piece.x + (x_dir*4))
        y_stop: int = (piece.y + (y_dir*4))

        d_pieces: List[ConnectFourPiece] = []

        while (x_offset != x_stop and x_offset not in (-1, BOARD_WIDTH)) and (y_offset != y_stop and y_offset not in (-1, BOARD_HEIGHT)):
            d_piece = self.pieces[x_offset][y_offset]
            if d_piece and d_piece.user_id == piece.user_id:
                d_pieces.append(d_piece)
            else:
                break

            if len(d_pieces) == 4:
                break

            x_offset += x_dir
            y_offset += y_dir

        return d_pieces

    
    def create_connect_four(self, pieces: List[ConnectFourPiece]) -> None:
        self.is_connect_four = True
        for piece in pieces:
            piece.replace_with(piece.user_id, WIN_PIECE)
