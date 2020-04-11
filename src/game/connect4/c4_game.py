from discord import TextChannel

from .c4_grid import ConnectFourGrid
from .connect_four_renderer import ConnectFourRenderer
from ...core.bunk_user import BunkUser


"""
Instance of a game itself - connected to
a creator and parent channel similar to hangman
"""
class ConnectFourGame:
    def __init__(self, creator: BunkUser, channel: TextChannel):
        self.creator: BunkUser = creator
        self.renderer: ConnectFourRenderer = ConnectFourRenderer(channel)


    # start a new game and render a new grid
    # into the channel using the renderer
    async def start(self) -> None:
        grid: ConnectFourGrid = ConnectFourGrid()
        await self.renderer.create_game(grid)
