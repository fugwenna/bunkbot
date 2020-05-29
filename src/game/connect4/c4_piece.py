from typing import List


"""
The 'ball' or 'bubble' the player will 
drop into the column of a grid board
"""
class ConnectFourPiece:
    def __init__(self, x: int, y: int, color: str):
        self.x: int = x
        self.y: int = y
        self.color: str = color
        self.user_id: int = None


    def replace_with(self, user_id: int, color: str) -> None:
        self.user_id = user_id
        self.color = color
