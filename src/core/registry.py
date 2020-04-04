from .error_log_service import ErrorLogService
from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_exception import BunkException
from ..chat.chat_service import ChatService
from ..core.constants import DB_TOKEN
from ..db.database_service import DatabaseService
from ..game.game_service import GameService
from ..user.role_service import RoleService
from ..user.sudo_service import SudoService
from ..user.user_service import UserService
from ..rpg.rpg_service import RpgService


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
RPG_SERVICE: RpgService = None


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
    global RPG_SERVICE

    logger = ErrorLogService()

    DATABASE_SERVICE = DatabaseService(bot, logger)
    CHANNEL_SERVICE = ChannelService(bot, DATABASE_SERVICE, logger)
    ROLE_SERVICE = RoleService(bot, DATABASE_SERVICE, CHANNEL_SERVICE)
    USER_SERVICE = UserService(bot, DATABASE_SERVICE, ROLE_SERVICE, CHANNEL_SERVICE)
    GAME_SERVICE = GameService(bot, DATABASE_SERVICE, CHANNEL_SERVICE, USER_SERVICE)
    SUDO_SERVICE = SudoService(bot, DATABASE_SERVICE, CHANNEL_SERVICE)
    CHAT_SERVICE = ChatService(bot, DATABASE_SERVICE, USER_SERVICE)
    RPG_SERVICE = RpgService(bot, DATABASE_SERVICE, USER_SERVICE)

    try:
        bot.run(DATABASE_SERVICE.get(DB_TOKEN))
    except ValueError as ex:
        print(logger.format_message(str(ex), "initialize", "ERROR"))
    except BunkException as bex:
        print(logger.format_message(bex.raw_message, "initialize", "ERROR"))
        logger.log_error(bex.raw_message, "initialize")
