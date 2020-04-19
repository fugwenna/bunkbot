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


    def update_piece(self, col_index: int, user_id: int, color: str) -> None:
        self.play_count += 1
        pieces: List[ConnectFourPiece] = self.pieces[col_index]

        for p in pieces:
            if p.user_id is None:
                p.replace_with(user_id, color)
                self.check_connect_four(p)
                break


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
        anchors_ru: List[ConnectFourPiece] = sorted(list(filter(lambda p: self.is_diagonal_from(piece, p, 1, 1), flat_pieces)), key=lambda s: s.x)
        anchors_rd: List[ConnectFourPiece] = sorted(list(filter(lambda p: self.is_diagonal_from(piece, p, 1, -1), flat_pieces)), key=lambda s: s.x)
        anchors_lu: List[ConnectFourPiece] = sorted(list(filter(lambda p: self.is_diagonal_from(piece, p, -1, 1), flat_pieces)), key=lambda s: s.x)
        anchors_ld: List[ConnectFourPiece] = sorted(list(filter(lambda p: self.is_diagonal_from(piece, p, -1, -1), flat_pieces)), key=lambda s: s.x)
        dpru: List[ConnectFourPiece] = self.loop_and_get_pieces(piece.user_id, anchors_ru, 0, len(anchors_ru), 1, False)
        dprd: List[ConnectFourPiece] = self.loop_and_get_pieces(piece.user_id, anchors_rd, 0, len(anchors_rd), 1, False)
        dplu: List[ConnectFourPiece] = self.loop_and_get_pieces(piece.user_id, anchors_lu, 0, len(anchors_lu), 1, False)
        dpld: List[ConnectFourPiece] = self.loop_and_get_pieces(piece.user_id, anchors_ld, 0, len(anchors_ld), 1, False)
        return set([piece]+dpru+dprd+dplu+dpld)
        

    def is_diagonal_from(self, piece: ConnectFourPiece, p_ref: ConnectFourPiece, dir_x: int, dir_y: int) -> None:
        return (
            ((p_ref.x == piece.x + (dir_x*1)) and (p_ref.y == piece.y + (dir_y*1))) or
            ((p_ref.x == piece.x + (dir_x*2)) and (p_ref.y == piece.y + (dir_y*2))) or
            ((p_ref.x == piece.x + (dir_x*3)) and (p_ref.y == piece.y + (dir_y*3))) or
            ((p_ref.x == piece.x + (dir_x*4)) and (p_ref.y == piece.y + (dir_y*4)))
        )


    def loop_and_get_pieces(self, user_id: int, anchors: List[ConnectFourPiece], start: int, stop: int, direction: int, do_break: bool = True) -> List[ConnectFourPiece]:
        pieces: List[ConnectFourPiece] = []

        for i in range(start, stop, direction):
            piece: ConnectFourPiece = anchors[i]

            if piece.user_id == user_id:
                pieces.append(piece)
            else:
                if do_break:
                    break

            if len(pieces) == 4:
                return pieces

        return pieces

    
    def create_connect_four(self, pieces: List[ConnectFourPiece]) -> None:
        self.is_connect_four = True
        for piece in pieces:
            piece.replace_with(piece.user_id, WIN_PIECE)
