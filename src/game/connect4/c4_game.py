from discord import TextChannel, Message

from .c4_constants import PLAYER1_PIECE, PLAYER2_PIECE
from .c4_board import ConnectFourBoard
from .c4_renderer import ConnectFourRenderer
from ..custom_game import CustomGame
from ...core.bunk_user import BunkUser


"""
Instance of a game itself - connected to
a creator and parent channel similar to hangman
"""
class ConnectFourGame(CustomGame):
    def __init__(self, creator: BunkUser, channel: TextChannel):
        super().__init__(channel, creator)
        self.opponent: BunkUser = None
        self.board: ConnectFourBoard = None
        self.renderer: ConnectFourRenderer = ConnectFourRenderer(channel)


    # start a new game and render a new grid
    # into the channel using the renderer
    async def start(self) -> None:
        self.board = ConnectFourBoard()
        await self.renderer.create_game(self.board, self.creator)


    async def update(self, message: Message, user: BunkUser) -> None:
        if not await self.is_cancel(message, self.creator):
            if self.renderer.player_one and self.renderer.player_two:
                if user.id not in [self.renderer.player_one.id, self.renderer.player_two.id]:
                    return

            player_id: int = message.author.id
            piece: str = (PLAYER1_PIECE, PLAYER2_PIECE)[player_id == self.creator.id]
            content: str = self.get_content(message)
            is_bad_option: bool = len(content) > 1 or not content.isdigit() or int(content) > 7

            if not is_bad_option:
                updated: bool = self.board.update_piece(int(content)-1, player_id, piece)
                if updated:
                    await self.renderer.update_board(self.board, False, user)

            self.is_complete = self.board.is_connect_four
