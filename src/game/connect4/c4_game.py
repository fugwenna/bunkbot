from discord import TextChannel, Message

from .c4_constants import PLAYER1_PIECE, PLAYER2_PIECE
from .c4_grid import ConnectFourGrid
from .c4_renderer import ConnectFourRenderer
from ..custom_game import CustomGame
from ...core.bunk_user import BunkUser


"""
Instance of a game itself - connected to
a creator and parent channel similar to hangman
"""
class ConnectFourGame(CustomGame):
    def __init__(self, creator: BunkUser, channel: TextChannel):
        super().__init__(channel)
        self.creator: BunkUser = creator
        self.opponent: BunkUser = None
        self.grid: ConnectFourGrid = None
        self.renderer: ConnectFourRenderer = ConnectFourRenderer(channel)


    # start a new game and render a new grid
    # into the channel using the renderer
    async def start(self) -> None:
        self.grid = ConnectFourGrid()
        await self.renderer.create_game(self.grid, self.creator)


    async def update(self, message: Message) -> None:
        if not await self.is_cancel(message):
            content: str = self.get_content(message)
            is_bad_option: bool = len(content) > 1 or not content.isdigit() or int(content) > 7

            if not is_bad_option:
                self.grid.update_piece(int(content)-1, self.creator.id, PLAYER1_PIECE)
                await self.renderer.update_board(self.grid)
