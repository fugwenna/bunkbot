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
        self.channel: TextChannel = channel
        self.set_defaults()


    @property
    def is_player_ones_turn(self) -> bool:
        if not self.player_one or not self.current_player_move_id:
            return False

        return True if self.player_one.id == self.current_player_move_id else False

    
    def set_defaults(self, reset_p1: bool = True) -> None:
        self.current_player_move_id: None
        self.player_two: BunkUser = None
        self.last_move_by: BunkUser = None
        self.new_game_message: Message = None
        self.board: Message = None

        if reset_p1:
            self.player_one: BunkUser = None

    
    # render a blank game into the channel
    async def create_game(self, board: ConnectFourBoard, player_one: BunkUser) -> None:
        await self.channel.purge()
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
        self.last_move_by = player

        if player and (player.id != self.player_one.id):
            self.player_two = player

        if self.player_two:
            self.current_player_move_id = self.player_two.id if player.id == self.player_one.id else self.player_one.id

        # loop over each column and 
        # fill the row from the bottom up
        for i in range(BOARD_HEIGHT):
            row_content: str = ""
            for j in range(BOARD_WIDTH):
                cfp: ConnectFourPiece = board.pieces[j][i]
                row_content += cfp.color

            row_content = self.add_player_to_render(i, row_content, board)
            cols.append(row_content)

        if is_new:
            self.board = await self.channel.send(BOARD_TEMPLATE.format(*cols))
        else:
            if self.new_game_message is not None:
                await self.new_game_message.delete()
                self.new_game_message = None
            await self.board.edit(content=BOARD_TEMPLATE.format(*cols))
        
        await self.update_board_for_turn(board)


    # show the player names and colors next to the board
    def add_player_to_render(self, position: int, content: str, board: ConnectFourBoard) -> str:
        player_two_str: str = self.player_two.name if self.player_two else ":ghost:"

        if position == 5:
            content += "\t\t\t Players:"
        elif position == 4:
            content += self.bold_name_if_turn("{0}  {1}".format(PLAYER1_PIECE, self.player_one.name), self.is_player_ones_turn, board.is_connect_four)
        elif position == 3:
            content += self.bold_name_if_turn("{0}  {1}".format(PLAYER2_PIECE, player_two_str), not self.is_player_ones_turn, board.is_connect_four)

        return content


    def bold_name_if_turn(self, name: str, is_turn: bool, is_win: bool) -> str:
        if not is_win and self.player_two and is_turn:
            return "\t\t\t **{0}**".format(name)

        return "\t\t\t {0}".format(name)


    # disable the ability for the opposing player
    # to enter anyything while it is not their turn
    async def update_board_for_turn(self, board: ConnectFourBoard) -> None:
        ow: dict = self.channel.overwrites

        if self.player_one:
            allow = not board.is_connect_four and self.is_player_ones_turn 
            if board.play_count == 1 and self.last_move_by.id == self.player_one.id:
                allow = False

            ow[self.player_one.member] = PermissionOverwrite(read_messages=True, send_messages=allow)

        if self.player_two:
            allow = not board.is_connect_four and (not self.is_player_ones_turn)
            ow[self.player_two.member] = PermissionOverwrite(read_messages=True, send_messages=allow)

        if board.is_connect_four:
            ow[self.channel.guild.default_role] = PermissionOverwrite(read_messages=True, send_messages=False)

        await self.channel.edit(overwrites=ow)

        if board.is_connect_four:
            await self.channel.send("CONNECT FOUR {0} !!!!".format(self.last_move_by.mention))
            await self.channel.send("This game will close in 10 seconds")
