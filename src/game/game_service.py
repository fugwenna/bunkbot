from discord import Game, Member, TextChannel, PermissionOverwrite
from random import randint

from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_user import BunkUser
from ..core.daemon import DaemonHelper
from ..core.functions import roll_int
from ..core.service import Service
from ..db.database_service import DatabaseService
from ..user.user_service import UserService


CHANCE_TO_UPDATE_ON_NEW_GAME: int = 70
INTERVAL_TO_UPDATE_GAME: int = 60


"""
Service specifically designed to deal with things like
setting BunkBot's played game, twitch streams, etc.
"""
class GameService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService, channels: ChannelService, users: UserService):
        super().__init__(bot, database)
        self.channels: ChannelService = channels
        self.users: UserService = users
        self.bot.on_initialized += self.set_game
        self.bot.on_initialized += self.check_streams
        self.bot.on_user_update += self.collect_game_from_user
        DaemonHelper.add(self.set_game, trigger="interval", minutes=INTERVAL_TO_UPDATE_GAME)


    # when a user is updated check if the game is currently in the 
    # database - if not, add it for later use
    async def collect_game_from_user(self, old_ref: Member, member: Member) -> None:
        bunk_user: BunkUser = self.users.get_by_id(member.id)

        if bunk_user is not None and bunk_user.is_gaming:
            game: Game = bunk_user.member.activity
            added = self.database.collect_game(game)

            if added:
                await self.channels.log_info("Added new game to database: `{0}`".format(game.name))
                await self.set_game()


    # every so often, set the bot status - if the bot
    # has decided to go "away" or do something else, do
    # not wire any game 
    async def set_game(self, force: bool = False) -> None:
        will_set = randint(0, 100) <= CHANCE_TO_UPDATE_ON_NEW_GAME

        if not force and will_set:
            games = self.database.game_names.all()

            if len(games) > 0:
                index = roll_int(0, len(games) - 1)
                game = games[index]

                await self.bot.change_presence(activity=Game(game["name"]))


    # do an initial check of current streams and update
    # the list in the stream channel
    async def check_streams(self) -> None:
        # TODO - currently disabled until the twitch API is fixed
        pass


    # for custom bunkbot games, create a new channel under the 'custom games'
    # category with a selectd prefix
    async def create_game_channel(self, name: str, user: BunkUser) -> TextChannel:
        channel: TextChannel = None

        if self.channels.CUSTOM_GAMES is not None:
            c_name: str = "{0}-{1}".format(name, user.name)

            bot_role_id: int = 437263429057773608 # TODO - config
            t = 699395055990997042
            ow: dict = { 
                self.bot.server.default_role: PermissionOverwrite(read_messages=False, send_messages=False),
                self.bot.server.get_member(user.id): PermissionOverwrite(read_messages=True, send_messages=True),
                self.server.get_role(bot_role_id): PermissionOverwrite(read_messages=True, send_messages=True),
                self.server.get_role(t): PermissionOverwrite(read_messages=True, send_messages=True)
            }

            count: int = len([c for c in self.channels.CUSTOM_GAMES.channels if c.name == c_name])
            if count > 0:
                c_name += "_{0}".format(count)

            channel = await self.channels.CUSTOM_GAMES.create_text_channel(c_name, overwrites=ow)
        else:
            await self.channels.log_error("Cannot create custom game - CUSTOM-GAMES channel cannot be found", "GameService")

        return channel


    def is_game_channel(self, game_name: str, channel_name: str, user_name: str) -> bool:
        channel_split: str = channel_name.split("-")
        channel_game_name: str = channel_split[0]
        channel_user: str = channel_split[1].split("_")[0]

        actual_name: str = "{0}-{1}".format(channel_game_name, channel_user)
        target_name: str = "{0}-{1}".format(game_name, user_name)

        return actual_name == target_name
