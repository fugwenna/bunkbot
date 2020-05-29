from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..channel.log_service import LogService
from ..chat.chat_service import ChatService
from ..db.database_service import DatabaseService
from ..etc.config_service import ConfigService
from ..game.game_service import GameService
from ..rpg.rpg_service import RpgService
from ..user.role_service import RoleService
from ..user.sudo_service import SudoService
from ..user.user_service import UserService
from ..weather.weather_service import WeatherService


"""
'DI' singletons for cogs so that stored refs are persisted
"""
CHANNEL_SERVICE: ChannelService = None
CHAT_SERVICE: ChatService = None
DATABASE_SERVICE: DatabaseService = None
GAME_SERVICE: GameService = None
ROLE_SERVICE: RoleService = None
RPG_SERVICE: RpgService = None
SUDO_SERVICE: SudoService = None
USER_SERVICE: UserService = None
WEATHER_SERVICE: WeatherService = None


"""
On bot load, initialize each keyword defined
service with the instance of the bot
"""
def initialize(bot: BunkBot) -> None:
    global CHANNEL_SERVICE
    global CHAT_SERVICE
    global DATABASE_SERVICE
    global GAME_SERVICE
    global SUDO_SERVICE
    global ROLE_SERVICE
    global RPG_SERVICE
    global USER_SERVICE
    global WEATHER_SERVICE

    DATABASE_SERVICE = DatabaseService(bot)
    CHANNEL_SERVICE = ChannelService(bot, DATABASE_SERVICE)
    ROLE_SERVICE = RoleService(bot, DATABASE_SERVICE, CHANNEL_SERVICE)
    USER_SERVICE = UserService(bot, DATABASE_SERVICE, ROLE_SERVICE, CHANNEL_SERVICE)
    GAME_SERVICE = GameService(bot, DATABASE_SERVICE, CHANNEL_SERVICE, USER_SERVICE)
    SUDO_SERVICE = SudoService(bot, DATABASE_SERVICE, CHANNEL_SERVICE)
    CHAT_SERVICE = ChatService(bot, DATABASE_SERVICE, USER_SERVICE, CHANNEL_SERVICE)
    RPG_SERVICE = RpgService(bot, DATABASE_SERVICE, USER_SERVICE)
    WEATHER_SERVICE = WeatherService(bot, DATABASE_SERVICE, CHANNEL_SERVICE)

    try:
        bot.run(ConfigService().discord_token)
    except Exception as e:
        LogService().log_error(e, "initialize")
