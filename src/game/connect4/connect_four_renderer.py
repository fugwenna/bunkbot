from typing import List
from discord import Message, TextChannel

from .c4_constants import BOARD_TEMPLATE
from .c4_grid import ConnectFourGrid
from .c4_piece import ConnectFourPiece


"""
Primary renderer of the game itself - this will
use datamodel properties to display the pieces on the board
"""
class ConnectFourRenderer:
    def __init__(self, channel: TextChannel):
        self.channel: TextChannel = channel
        self.board: Message

    
    # render a blank game into the channel
    async def create_game(self, grid: ConnectFourGrid) -> None:
        await self.update_board()


    # when a player has entered a valid valud 
    # determined in the game instance, render the
    # updated pieces out into the channel
    async def update_board(self) -> None:
        rows: List[str] = []

        # loop over each column and 
        # fill the row from the bottom up
        for i in range(0, 5):
            row_content: str = ""
            rps: List[ConnectFourPiece] = sorted(
                filter(lambda p: p.coordinate.y == i), 
                key=lambda x: x.coordate.x, reverse=True)

            cfp: ConnectFourPiece
            for cfp in rps:
                print("{0},{1}".format(cfp.coordinate.x, cfp.coordinate.y))
