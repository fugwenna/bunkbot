from discord import Member
from discord.ext.commands import Context, Bot

from .models.event_hook import EventHook
from .util.cog_loader import get_cogs

"""
Main extended bot from discord.py which 
is the primary loaded instance from main.py

The primary use for this bot is essentially an event
emitter to the services which use this instance
"""

BOT_DESCRIPTION = """
The bunkest bot - type '!help' for my commands, or say my name to chat with me. 
Type '!help [command] for more info on a command (i.e. !help color)\n
"""
class BunkBot(Bot):
    def __init__(self):
        super().__init__("!", None, BOT_DESCRIPTION)
        self.on_initialized: EventHook = EventHook()
        self.on_user_update: EventHook = EventHook()
        self.on_user_remove: EventHook = EventHook()


    # lifecycle hook - set up all
    # of the necessary and useful channels
    async def load(self) -> None:
        for cog in get_cogs():
            self.load_extension(cog)

        await self.on_initialized.emit()


    # handle the event where discord 
    # updates a member
    async def handle_member_update(self, old: Member, new: Member) -> None:
        await self.on_user_update.emit(old, new)


    # handle the event where a user
    # is removed from the server (self or otherwise)
    async def handle_member_remove(self, member: Member) -> None:
        await self.on_user_remove.emit(member)


"""
Main instance which will be loaded into
the main.py __init__ function
"""
bunkbot = BunkBot()
