from typing import List
from .c4_coord import ConnectFourCoordinate

"""
The 'ball' or 'bubble' the player will 
drop into the column of a grid board
"""
class ConnectFourPiece:
    def __init__(self, coord: ConnectFourCoordinate, color: str):
        self.coordinate: ConnectFourCoordinate = coord
        self.color: str = color
        self.user_id: int = None
        self.connected_pieces: List[any] = []


    def replace_with(self, user_id: int, color: str) -> None:
        self.user_id = user_id
        self.color = color


    def check_if_connected(self, piece: any, pieces: List[any]) -> None:
        c_pieces: List[any] = []
        added: bool = self.is_ref(piece)
        is_connected = added == True

        if not added: 
            is_v = self.is_connected_vertical(piece)
            is_h = self.is_connected_horizontal(piece)
            is_d = self.is_connected_diagonal(piece)

            connected = is_v or is_h or is_d

            if connected:
                is_connected = True
                c_pieces.append(piece)
                refs: List[any] = []
                for ref in piece.connected_pieces:
                    if is_v:
                        pass
                    elif is_h:
                        pass
                    elif is_d:
                        pass

        self.connected_pieces = c_pieces
        return is_connected


    def is_ref(self, piece: any) -> bool:
        return next(
            (p for p in self.connected_pieces if 
            p.coordinate.x == piece.coordinate.x 
            and p.coordinate.y == piece.coordinate.y), None)
            

    def is_connected_vertical(self, piece: any) -> bool:
        return (
            (piece.coordinate.y == self.coordinate.y+1 and piece.coordinate.x == self.coordinate.x) or
            (piece.coordinate.y == self.coordinate.y-1 and piece.coordinate.x == self.coordinate.x))


    def is_connected_horizontal(self, piece: any) -> None:
        return (
            (piece.coordinate.y == self.coordinate.y and piece.coordinate.x == self.coordinate.x+1) or
            (piece.coordinate.y == self.coordinate.y and piece.coordinate.x == self.coordinate.x-1))


    def is_connected_diagonal(self, piece: any) -> None:
        return (
            (piece.coordinate.y == self.coordinate.y+1 and piece.coordinate.x == self.coordinate.x+1) or
            (piece.coordinate.y == self.coordinate.y-1 and piece.coordinate.x == self.coordinate.x+1) or
            (piece.coordinate.y == self.coordinate.y-1 and piece.coordinate.x == self.coordinate.x-1) or
            (piece.coordinate.y == self.coordinate.y+1 and piece.coordinate.x == self.coordinate.x-1))
