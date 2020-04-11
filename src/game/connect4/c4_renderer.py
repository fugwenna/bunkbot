from typing import List
from discord import Message, TextChannel

from .c4_constants import BOARD_TEMPLATE, BOARD_HEIGHT, PLAYER1_PIECE, PLAYER2_PIECE
from .c4_grid import ConnectFourGrid
from .c4_piece import ConnectFourPiece
from ...core.bunk_user import BunkUser


"""
Primary renderer of the game itself - this will
use datamodel properties to display the pieces on the board
"""
class ConnectFourRenderer:
    def __init__(self, channel: TextChannel):
        self.player_one: BunkUser = None
        self.player_two: BunkUser = None
        self.channel: TextChannel = channel
        self.new_game_message: Message = None
        self.board: Message = None

    
    # render a blank game into the channel
    async def create_game(self, grid: ConnectFourGrid, player_one: BunkUser) -> None:
        self.player_one = player_one

        ow = self.channel.overwrites
        await self.channel.edit(overwrites=ow, slowmode_delay=1)
        await self.update_board(grid, True)
        self.new_game_message = await self.channel.send("New ConnectFour Game! Waiting for another player...")


    # when a player has entered a valid valud 
    # determined in the game instance, render the
    # updated pieces out into the channel
    async def update_board(self, grid: ConnectFourGrid, is_new: bool = False) -> None:
        cols: List[str] = []

        # loop over each column and 
        # fill the row from the bottom up
        for i in range(0, BOARD_HEIGHT):
            row_content: str = ""
            rps: List[ConnectFourPiece] = sorted(
                filter(lambda p: p.coordinate.y == i, grid.pieces), 
                key=lambda x: x.coordinate.x)

            for j in range(0, len(rps)):
                cfp: ConnectFourPiece = rps[j]
                row_content += cfp.color

            row_content = self.add_player_to_render(i, row_content)
            cols.append(row_content)

        if is_new:
            self.board = await self.channel.send(BOARD_TEMPLATE.format(*cols))
        else:
            if self.new_game_message is not None:
                await self.new_game_message.delete()
                self.new_game_message = None
            await self.board.edit(content=BOARD_TEMPLATE.format(*cols))


    def add_player_to_render(self, position: int, content: str) -> str:
        if position == 5:
            content += "\t\t\t Players:"
        elif position == 4:
            content += "\t\t\t **{0}  {1}**".format(PLAYER1_PIECE, self.player_one.name)
        elif position == 3:
            content += "\t\t\t {0}  unknown".format(PLAYER2_PIECE)

        return content
