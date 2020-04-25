import time, threading, asyncio
from typing import List
from discord import Message, TextChannel
from discord.ext.commands import command, Context, Cog

from .hangman_game import HangmanGame
from ..custom_cog_model import CustomGameCog
from ..game_service import GameService
from ...bunkbot import BunkBot
from ...core.bunk_user import BunkUser
from ...core.registry import GAME_SERVICE


"""
Cog that will setup hangman games for people to play
"""
class HangmanCog(Cog, CustomGameCog):
    def __init__(self, bot: BunkBot, game_service: GameService):
        super().__init__(game_service)
        bot.on_user_message += self.get_answer
    

    @command(help="Create a game of hangman!", aliases=["hm"])
    async def hangman(self, ctx: Context) -> None:
        await self.start_new_game(ctx, "hangman", False)


    # @override
    def create_new_game(self, channel: TextChannel, user: BunkUser) -> HangmanGame:
        return HangmanGame(user, channel)


def setup(bot: BunkBot) -> None:
    bot.add_cog(HangmanCog(bot, GAME_SERVICE))
