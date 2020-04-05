from typing import List
import time, threading
from discord import PermissionOverwrite, Message, TextChannel
from discord.ext.commands import command, Context, Cog

from .hangman_renderer import HangmanRenderer
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
        self.games: List[HangmanRenderer] = []
        self.users: UserService = users
        self.database = database
        self.channels: ChannelService = channels
        self.bot.on_user_message += self.get_answer
    

    @command(help="Create a game of hangman!")
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
        if self.channels.HANGMAN is not None:
            bunk_user: BunkUser = self.users.get_by_id(ctx.author.id)
            channel_name: str = "hangman-{0}".format(bunk_user.name)
            exists = next((c for c in self.channels.HANGMAN.channels if c.name == channel_name), None)

            if exists is not None:
                await ctx.send("{0} - you already have a hangman game in channels `games/{1}` !".format(bunk_user.mention, channel_name))
            else:
                renderer: HangmanRenderer = HangmanRenderer(self.bot, bunk_user, self.channels.HANGMAN, self.users.users, channel_name)
                self.games.append(renderer)

                await renderer.start_game()
        else:
            await self.channels.log_error("Cannot create hangman game - HANGMAN channel cannot be found", "HangmanCog")


    # update the message of a given game - check if the
    # context of the message is a hangman channel 
    async def get_answer(self, message: Message) -> None:
        if not message.author.bot:
            channel_name: str = message.channel.name
            if channel_name.split("-")[0] == "hangman":
                ch: TextChannel = next((c for c in self.channels.HANGMAN.channels if c.name == channel_name), None)
                if ch is not None:
                    game: HangmanRenderer = next((h for h in self.games if h.channel.id == ch.id), None)
                    if game is not None:
                        await game.update(message)
                        if game.is_cancelled:
                            self.games.remove(game)
                        elif game.is_completed:
                            time.sleep(10)
                            await game.complete_game()
                            
                            for p in game.participants:
                                self.database.update_user(p.db_user)

                            #threading.Timer(15, self.complete_game, game)


    async def complete_game(self, game: HangmanRenderer) -> None:
        self.games.remove(game)
        await game.complete_game()


def setup(bot: BunkBot) -> None:
    bot.add_cog(HangmanCog(bot, CHANNEL_SERVICE, USER_SERVICE, DATABASE_SERVICE))
