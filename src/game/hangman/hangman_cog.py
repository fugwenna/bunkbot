import time, threading

from typing import List
from discord import PermissionOverwrite, Message, TextChannel
from discord.ext.commands import command, Context, Cog

from .hangman_game import HangmanGame
from ...bunkbot import BunkBot
from ...core.bunk_user import BunkUser
from ...core.registry import USER_SERVICE, CHANNEL_SERVICE, DATABASE_SERVICE
from ...db.database_service import DatabaseService
from ...channel.channel_service import ChannelService
from ...user.user_service import UserService


"""
Cog that will setup hangman games for people to play
"""
class HangmanCog(Cog):
    def __init__(self, bot: BunkBot, channels: ChannelService, users: UserService, database: DatabaseService):
        self.bot: BunkBot = bot
        self.games: List[HangmanGame] = []
        self.users: UserService = users
        self.database = database
        self.channels: ChannelService = channels
        self.bot.on_user_message += self.get_answer
    

    @command(help="Create a game of hangman!", aliases=["hm"])
    async def hangman(self, ctx: Context) -> None:
        try:
            if self.bot.server:
                await ctx.message.delete()
                await self.create_hangman_game(ctx)
            else:
                await self.channels.log_error("Cannot create hangman game with null server", "HangmanCog")
        except Exception as e:
            await self.channels.log_error(e, "hangman")


    # create the hangman game itself - check if a user
    # already has an existing game (they can always cancel)
    async def create_hangman_game(self, ctx: Context) -> None:
        if self.channels.CUSTOM_GAMES is not None:
            bunk_user: BunkUser = self.users.get_by_id(ctx.author.id)
            exists = next((c for c in self.games if c.creator.id == bunk_user.id), None)

            if exists is not None:
                await ctx.send("{0} - you already have an active hangman game!".format(bunk_user.mention))
            else:
                game = HangmanGame(bunk_user)
                self.games.append(game)

                await game.start(self.channels.CUSTOM_GAMES)
        else:
            await self.channels.log_error("Cannot create hangman game - CUSTOM_GAMES channel cannot be found", "HangmanCog")


    # update the message of a given game - check if the
    # context of the message is a hangman channel 
    async def get_answer(self, message: Message) -> None:
        if not message.author.bot:
            channel_name: str = message.channel.name
            if channel_name.split("-")[0] == "hangman":
                ch: TextChannel = next((c for c in self.channels.CUSTOM_GAMES.channels if c.name == channel_name), None)
                if ch is not None:
                    game: HangmanGame = next((h for h in self.games if h.renderer.channel.id == ch.id), None)
                    if game is not None:
                        await game.update(message)
                        if game.is_cancelled:
                            self.games.remove(game)


def setup(bot: BunkBot) -> None:
    bot.add_cog(HangmanCog(bot, CHANNEL_SERVICE, USER_SERVICE, DATABASE_SERVICE))
