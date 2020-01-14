from .error_log_service import ErrorLogService
from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..chat.chat_service import ChatService
from ..core.constants import DB_TOKEN
from ..db.database_service import DatabaseService
from ..game.game_service import GameService
from ..user.role_service import RoleService
from ..user.sudo_service import SudoService
from ..user.user_service import UserService


"""
'DI' singletons for cogs so that stored refs are persisted
"""
DATABASE_SERVICE: DatabaseService = None
CHANNEL_SERVICE: ChannelService = None
CHAT_SERVICE: ChatService = None
GAME_SERVICE: GameService = None
ROLE_SERVICE: RoleService = None
SUDO_SERVICE: SudoService = None
USER_SERVICE: UserService = None


"""
On bot load, initialize each keyword defined
service with the instance of the bot
"""
def initialize(bot: BunkBot) -> None:
    global DATABASE_SERVICE
    global CHANNEL_SERVICE
    global CHAT_SERVICE
    global ROLE_SERVICE
    global SUDO_SERVICE
    global USER_SERVICE
    global GAME_SERVICE

    DATABASE_SERVICE = DatabaseService(bot)
    CHANNEL_SERVICE = ChannelService(bot, DATABASE_SERVICE, ErrorLogService())
    ROLE_SERVICE = RoleService(bot, DATABASE_SERVICE)
    USER_SERVICE = UserService(bot, DATABASE_SERVICE, ROLE_SERVICE, CHANNEL_SERVICE)
    GAME_SERVICE = GameService(bot, DATABASE_SERVICE, CHANNEL_SERVICE, USER_SERVICE)
    SUDO_SERVICE = SudoService(bot, DATABASE_SERVICE, CHANNEL_SERVICE)
    CHAT_SERVICE = ChatService(bot, DATABASE_SERVICE)

    bot.run(DATABASE_SERVICE.get(DB_TOKEN))
