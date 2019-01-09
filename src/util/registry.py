from ..db.db import database
from ..util.constants import DB_TOKEN
from ..bunkbot import BunkBot
from ..services.channel_service import ChannelService
from ..services.chat_service import ChatService
from ..services.role_service import RoleService
from ..services.sudo_service import SudoService
from ..services.user_service import UserService

"""
'DI' singletons for cogs so that stored refs are persisted
"""
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
    global CHANNEL_SERVICE
    global CHAT_SERVICE
    global ROLE_SERVICE
    global SUDO_SERVICE
    global USER_SERVICE

    CHANNEL_SERVICE = ChannelService(bot)
    CHAT_SERVICE = ChatService(bot)
    ROLE_SERVICE = RoleService(bot)
    SUDO_SERVICE = SudoService(bot)
    USER_SERVICE = UserService(bot)
    bot.run(database.get(DB_TOKEN))