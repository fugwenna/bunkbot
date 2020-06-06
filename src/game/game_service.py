from discord import Game, Member, TextChannel, CategoryChannel, PermissionOverwrite, Message, Status, ActivityType
from random import randint

from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_user import BunkUser
from ..core.daemon import DaemonHelper
from ..core.functions import will_execute_on_chance, get_current_hour
from ..core.service import Service
from ..db.database_service import DatabaseService
from ..user.user_service import UserService


CHANCE_TO_GO_IDLE: int = 25
CHANCE_TO_UPDATE_ON_NEW_GAME: int = 80
CHANCE_TO_DO_NOTHING: int = 40
CHANCE_TO_GO_DND: int = 1
INTERVAL_TO_UPDATE_IDLE: int = 120
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
        self.config.raise_error_on_bad_config = False
        self.bot.on_initialized += self.go_idle
        self.bot.on_initialized += self.check_streams
        self.bot.on_user_update += self.collect_game_from_user
        DaemonHelper.add(self.set_game, trigger="interval", minutes=INTERVAL_TO_UPDATE_GAME)
        DaemonHelper.add(self.go_idle, trigger="interval", minutes=INTERVAL_TO_UPDATE_IDLE)


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
    async def set_game(self) -> None:
        do_nothing: bool = will_execute_on_chance(CHANCE_TO_DO_NOTHING)
        go_dnd: bool = will_execute_on_chance(CHANCE_TO_GO_DND)
        play_game: bool = will_execute_on_chance(CHANCE_TO_UPDATE_ON_NEW_GAME)

        if play_game:
            games = self.database.game_names.all()

            if len(games) > 0:
                index = randint(0, len(games) - 1)
                game = games[index]

                await self.bot.change_presence(status=Status.online, activity=Game(game["name"]))
        elif do_nothing:
            await self.bot.change_presence(status=None, activity=None)
        elif go_dnd:
            await self.bot.change_presence(status=Status.dnd, activity=None)



    # every so often, let bunky take a break. he does hard work
    async def go_idle(self) -> None:
        if self.bot.member_ref.status != Status.idle:
            hour: int = get_current_hour()
            is_sleepy_time = hour <= 8 or hour >= 12
            go_idle: bool = is_sleepy_time or will_execute_on_chance(CHANCE_TO_GO_IDLE)

            if go_idle:
                await self.bot.change_presence(status=Status.idle, activity=None)
            elif self.bot.member_ref.activity is None:
                await self.set_game()
        else:
            await self.set_game()


    # do an initial check of current streams and update
    # the list in the stream channel
    async def check_streams(self) -> None:
        # TODO - currently disabled until the twitch API is fixed
        pass


    # for custom bunkbot games, create a new channel under the 'custom games'
    # category with a selectd prefix
    async def create_game_channel(self, name: str, user: BunkUser, all_users: bool = True) -> TextChannel:
        channel: TextChannel = None
        game_channel: str = self.config.custom_games_channel

        if game_channel is not None:
            gc_ref: TextChannel = await self.channels.get_by_name(game_channel)
            c_name: str = "{0}-{1}".format(name, user.name)

            ow: dict = { 
                self.server.default_role: PermissionOverwrite(read_messages=all_users, send_messages=all_users),
                self.server.get_member(user.id): PermissionOverwrite(read_messages=True, send_messages=True),
                self.server.get_member(self.bot.user.id): PermissionOverwrite(read_messages=True, send_messages=True)
            }

            if gc_ref is not None:
                is_cat: bool = isinstance(gc_ref, CategoryChannel)

                if not is_cat:
                    await self.channels.log_error("Cannot create game under a non-category channel.", "GameService")
                else:
                    c_name = self.get_game_name(gc_ref, c_name)
                    channel = await gc_ref.create_text_channel(c_name, overwrites=ow, slowmode_delay=1)
            else:
                c_name = self.get_game_name(None, c_name)
                channel = await self.bot.server.create_text_channel(c_name, overwrites=ow, slowmode_delay=1)
        else:
            await self.channels.log_error("Cannot create custom game - CUSTOM-GAMES channel cannot be found", "GameService")

        return channel


    def get_game_name(self, gc_ref: CategoryChannel, c_name: str) -> str:
        count: int = len([c for c in self.bot.server.channels if c.name == c_name])

        if count > 0:
            c_name += "_{0}".format(count)

        return c_name
