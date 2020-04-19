from typing import List
from discord import Message, TextChannel, PermissionOverwrite

from .c4_constants import BOARD_TEMPLATE, BOARD_HEIGHT, BOARD_WIDTH, PLAYER1_PIECE, PLAYER2_PIECE
from .c4_board import ConnectFourBoard
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


    @property
    def is_player_ones_turn(self) -> bool:
        if not self.player_one or not self.current_player_move_id:
            return False

        return True if self.player_one.id == self.current_player_move_id else False

    
    # render a blank game into the channel
    async def create_game(self, board: ConnectFourBoard, player_one: BunkUser) -> None:
        self.player_one = player_one
        self.current_player_move_id = player_one.id

        ow = self.channel.overwrites
        await self.channel.edit(overwrites=ow, slowmode_delay=1)
        await self.update_board(board, True, None)
        self.new_game_message = await self.channel.send("New ConnectFour Game! Waiting for another player...")


    # when a player has entered a valid valud 
    # determined in the game instance, render the
    # updated pieces out into the channel
    async def update_board(self, board: ConnectFourBoard, is_new: bool, player: BunkUser) -> None:
        cols: List[str] = []

        if player and (player.id != self.player_one.id):
            self.player_two = player

        if self.player_two:
            self.current_player_move_id = self.player_two.id if player.id == self.player_one.id else self.player_one.id

        # loop over each column and 
        # fill the row from the bottom up
        for i in range(BOARD_HEIGHT):
            row_content: str = ""
            for j in range(BOARD_WIDTH):
                cfp: ConnectFourPiece = board.pieces[i][j]
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
        
        await self.update_board_for_turn()


    # show the player names and colors next to the board
    def add_player_to_render(self, position: int, content: str) -> str:
        player_two_str: str = self.player_two.name if self.player_two else ":ghost:"

        if position == 5:
            content += "\t\t\t Players:"
        elif position == 4:
            content += self.bold_name_if_turn("{0}  {1}".format(PLAYER1_PIECE, self.player_one.name), self.is_player_ones_turn)
        elif position == 3:
            content += self.bold_name_if_turn("{0}  {1}".format(PLAYER2_PIECE, player_two_str), not self.is_player_ones_turn)

        return content


    def bold_name_if_turn(self, name: str, is_turn: bool) -> str:
        if self.player_two and is_turn:
            return "\t\t\t **{0}**".format(name)

        return "\t\t\t {0}".format(name)


    # disable the ability for the opposing player
    # to enter anyything while it is not their turn
    async def update_board_for_turn(self) -> None:
        ow: dict = self.channel.overwrites

        if self.player_one:
            ow[self.player_one.member] = PermissionOverwrite(read_messages=True, send_messages=self.is_player_ones_turn)

        if self.player_two:
            ow[self.player_two.member] = PermissionOverwrite(read_messages=True, send_messages=(not self.is_player_ones_turn))

        await self.channel.edit(overwrites=ow)
