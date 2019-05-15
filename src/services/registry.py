from src.bunkbot import BunkBot
from src.util.constants import DB_TOKEN
from src.services.database_service import DatabaseService
from src.services.channel_service import ChannelService
from src.services.chat_service import ChatService
from src.services.role_service import RoleService
from src.services.sudo_service import SudoService
from src.services.user_service import UserService
from src.services.game_service import GameService

"""
'DI' singletons for cogs so that stored refs are persisted
"""
DATABASE_SERVICE: DatabaseService = None
CHANNEL_SERVICE: ChannelService = None
CHAT_SERVICE: ChatService = None
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
    CHANNEL_SERVICE = ChannelService(bot, DATABASE_SERVICE)
    GAME_SERVICE = GameService(bot, DATABASE_SERVICE, CHANNEL_SERVICE)
    CHAT_SERVICE = ChatService(bot, DATABASE_SERVICE)
    ROLE_SERVICE = RoleService(bot, DATABASE_SERVICE)
    SUDO_SERVICE = SudoService(bot, DATABASE_SERVICE)
    USER_SERVICE = UserService(bot, DATABASE_SERVICE)
    bot.run(DATABASE_SERVICE.get(DB_TOKEN))
