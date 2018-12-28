from discord.ext import commands
from .services.user_service import UserService
from .services.role_service import RoleService
from .services.channel_service import ChannelService
from .services.chat_service import ChatService
from .services.sudo_service import SudoService

"""
Main extended bot from discord.py which 
is the primary loaded instance from main.py
"""

BOT_DESCRIPTION = """
The bunkest bot - type '!help' for my commands, or say my name to chat with me. 
Type '!help [command] for more info on a command (i.e. !help color)\n
"""
class BunkBot(commands.Bot):
    def __init__(self,
                 users: UserService,
                 roles: RoleService,
                 channels: ChannelService,
                 chat: ChatService,
                 sudo: SudoService):
        super().__init__("!", None, BOT_DESCRIPTION, True)

        self.users: UserService = users
        self.roles: RoleService = roles
        self.channels: ChannelService = channels
        self.chat: ChatService = chat
        self.sudo: SudoService = sudo


    # lifecycle hook - set up all
    # of the necessary and useful channels
    async def on_init(self) -> None:
        try:
            server = self.get_server("")#database.get(DB_SERVER_ID))
            self.users.load(server)
            self.role.load(server)
            self.channels.load(server)
            self.chat.load(server)
            self.sudo.load(server)
        except Exception:
            return


"""
Main instance which will be loaded into
the main.py __init__ function
"""
bunkbot = BunkBot(
    UserService(),
    RoleService(),
    ChannelService(),
    ChatService(),
    SudoService()
)
