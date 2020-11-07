from discord import Member, Guild, Message, Intents
from discord.ext.commands import Context, Bot, DefaultHelpCommand

from .core.bunk_user import BunkUser
from .core.cog_loader import get_cogs
from .core.event_hook import EventHook
from .core.functions import simple_string


INTENTS = Intents().default()
INTENTS.members = True
INTENTS.presences = True


BOT_DESCRIPTION = """
The bunkest bot - type '!help' for my commands, or say my name to chat with me. 
Type '!help [command] for more info on a command (i.e. !help color)\n
"""


class BunkBot(Bot):
    """
    Main extended bot from discord.py which 
    is the primary loaded instance from main.py

    The primary use for this bot is essentially an event
    emitter to the services which use this instance

    Attributes
    -----------
    on_initialized: EventHook
        Fired after the bot has fully loaded from the on_ready built-in event

    on_user_joined: EventHook
        Fired after a user has joined the server 

    on_user_update: EventHook
        Fired when a user has updated metadata of their profiles 

    on_user_remove: EventHook
        Fired when a user has been removed (or leaves) the server 

    on_user_message: EventHook
        Fired when a user has sent a message to the server

    ADMIN_USER: BunkUser
        Represents the owner of the guild/server

    server: Guild
        Assumed single guild/server the bot resides

    member_ref: Member
        Reference to the discord member to which the bot belongs

    name: str
        Name of the bot

    name_lower: str
        Name of the bot (lowercase)
    """

    def __init__(self):
        super().__init__("!", DefaultHelpCommand(dm_help=True), BOT_DESCRIPTION, intents=INTENTS)
        self.on_initialized: EventHook = EventHook()
        self.on_user_joined: EventHook = EventHook()
        self.on_user_update: EventHook = EventHook()
        self.on_user_remove: EventHook = EventHook()
        self.on_user_message: EventHook = EventHook()
        self.ADMIN_USER: BunkUser = None
        self.server: Guild = None
        self.member_ref: Member
        self.name: str = None
        self.name_lower: str = None


    async def load(self) -> None:
        """
        Lifecycle hook - set up all of the necessary and useful channels. 
        The `on_initialized` event is heard from any class inheriting the Service
        class and setup in the global [core/]registry
        """
        for cog in get_cogs():
            self.load_extension(cog)

        self.server = self.guilds[0] # assume privately loaded bot
        self.member_ref = self.server.get_member(self.user.id)
        self.name = simple_string(self.member_ref.name, False)
        self.name_lower = self.name.lower()

        await self.on_initialized.emit()


    async def handle_member_join(self, new: Member) -> None:
        """
        Handle the event where a new user joins the server

        Parameters
        -----------
        new: Member
            The new member who has joined the server
        """
        await self.on_user_joined.emit(new)


    async def handle_member_update(self, old: Member, new: Member) -> None:
        """
        Handle the event where discord updates a member

        Parameters
        -----------
        old: Member
            Original reference to the member before update

        new: Member
            Updated discord server member
        """
        await self.on_user_update.emit(old, new)


    async def handle_member_remove(self, member: Member) -> None:
        """
        Handle the event where a user is removed from the server (self or otherwise)

        Parameters
        -----------
        member: Member
            Member which has been removed from the server
        """
        await self.on_user_remove.emit(member)


    async def handle_message(self, message: Message) -> None:
        """
        handle the vent when a
        message is sent 
        """
        await self.on_user_message.emit(message)


"""
Main instance which will be loaded into
the main.py __init__ function
"""
bunkbot = BunkBot()
