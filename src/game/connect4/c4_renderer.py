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
        self.current_player_move_id: None
        self.player_one: BunkUser = None
        self.player_two: BunkUser = None
        self.channel: TextChannel = channel
        self.new_game_message: Message = None
        self.board: Message = None

    
    # render a blank game into the channel
    async def create_game(self, grid: ConnectFourGrid, player_one: BunkUser) -> None:
        self.player_one = player_one
        self.current_player_move_id = player_one.id

        ow = self.channel.overwrites
        await self.channel.edit(overwrites=ow, slowmode_delay=1)
        await self.update_board(grid, True, None)
        self.new_game_message = await self.channel.send("New ConnectFour Game! Waiting for another player...")


    # when a player has entered a valid valud 
    # determined in the game instance, render the
    # updated pieces out into the channel
    async def update_board(self, grid: ConnectFourGrid, is_new: bool, player: BunkUser) -> None:
        cols: List[str] = []

        if player and (player.id != self.player_one.id):
            self.player_two = player

        if self.player_two:
            self.current_player_move_id = self.player_two.id if player.id == self.player_one.id else self.player_one.id

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
        
        #await self.update_board_for_turn()


    # show the player names and colors next to the board
    def add_player_to_render(self, position: int, content: str) -> str:
        is_player_one_turn: bool = False
        player_two_str: str = self.player_two.name if self.player_two else ":ghost:"

        if self.player_two:
            is_player_one_turn = True if self.player_one.id == self.current_player_move_id else False
        else:
            is_player_one_turn = True

        if position == 5:
            content += "\t\t\t Players:"
        elif position == 4:
            content += self.bold_name_if_turn("{0}  {1}".format(PLAYER1_PIECE, self.player_one.name), is_player_one_turn)
        elif position == 3:
            content += self.bold_name_if_turn("{0}  {1}".format(PLAYER2_PIECE, player_two_str), not is_player_one_turn)

        return content


    def bold_name_if_turn(self, name: str, is_turn: bool) -> str:
        if self.player_two and is_turn:
            return "\t\t\t **{0}**".format(name)

        return "\t\t\t {0}".format(name)


    # disable the ability for the opposing player
    # to enter anyything while it is not their turn
    async def update_board_for_turn(self) -> None:
        pass
