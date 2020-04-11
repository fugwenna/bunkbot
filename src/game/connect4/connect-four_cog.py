from typing import List
from discord import Message, TextChannel
from discord.ext.commands import command, Context, Cog

from .c4_game import ConnectFourGame
from ..game_service import GameService
from ...bunkbot import BunkBot
from ...core.bunk_user import BunkUser
from ...core.registry import GAME_SERVICE
from ...channel.channel_service import ChannelService
from ...user.user_service import UserService


"""
Cog that will setup connect four games
"""
class ConnectFourCog(Cog):
    def __init__(self, game_service: GameService):
        self.game_service: GameService = game_service
        self.games: List[ConnectFourGame] = []


    @command(help="Create a game of connect four!", aliases=["c4"])
    async def connectfour(self, ctx: Context) -> None:
        user: BunkUser = self.game_service.users.get_by_id(ctx.message.author.id)
        channel: TextChannel = await self.game_service.create_game_channel("connect4-{0}", user)
        game = ConnectFourGame(user, channel)
        await game.start()


    async def get_answer(self, message: Message) -> None:
        pass
    

def setup(bot: BunkBot) -> None:
    print("? lol yo")
    bot.add_cog(ConnectFourCog(GAME_SERVICE))
