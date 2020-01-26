from discord import Game, Member
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
            index = roll_int(0, len(games) - 1)
            game = games[index]

            await self.bot.change_presence(activity=Game(game["name"]))


    # do an initial check of current streams and update
    # the list in the stream channel
    async def check_streams(self) -> None:
        # TODO - currently disabled until the twitch API is fixed
        pass
