import asyncio
from typing import List
from discord import Message, TextChannel
from discord.ext.commands import command, Context, Cog

from .c4_game import ConnectFourGame
from ..custom_cog_model import CustomGameCog
from ..game_service import GameService
from ...bunkbot import BunkBot
from ...core.bunk_user import BunkUser
from ...core.registry import GAME_SERVICE


"""
Cog that will setup connect four games
"""
class ConnectFourCog(Cog, CustomGameCog):
    def __init__(self, bot: BunkBot, game_service: GameService):
        super().__init__(game_service)
        bot.on_user_message += self.get_answer


    @command(help="Create a game of connect four!", aliases=["c4"])
    async def connectfour(self, ctx: Context) -> None:
        await self.start_new_game(ctx, "connect4", True)


    # @override
    def create_new_game(self, channel: TextChannel, user: BunkUser) -> ConnectFourGame:
        return ConnectFourGame(user, channel)


def setup(bot: BunkBot) -> None:
    bot.add_cog(ConnectFourCog(bot, GAME_SERVICE))
