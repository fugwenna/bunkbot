from .c4_coord import ConnectFourCoordinate

"""
The 'ball' or 'bubble' the player will 
drop into the column of a grid board
"""
class ConnectFourPiece:
    def __init__(self, coord: ConnectFourCoordinate, color: str):
        self.coordinate: ConnectFourCoordinate = None
        self.color: str = color
        self.user_id: int = None


    def replace_with(self, user_id: int, color: str) -> None:
        self.user_id = user_id
        self.color = color

