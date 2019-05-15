from discord.ext.commands import Context, Bot
from src.util.cog_loader import get_cogs
from src.models.event_hook import EventHook

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
        super().__init__("!", None, BOT_DESCRIPTION, True)
        self.on_initialized: EventHook = EventHook()
        self.on_error: EventHook = EventHook()

    # lifecycle hook - set up all
    # of the necessary and useful channels
    async def load(self) -> None:
        for cog in get_cogs():
            self.load_extension(cog)

        await self.on_initialized.fire()

    # handle an error from a cog and
    # send a basic error message back
    async def handle_error(self, error: Exception, command: str, ctx: Context):
        await self.on_error.fire(error, command, ctx)


"""
Main instance which will be loaded into
the main.py __init__ function
"""
bunkbot = BunkBot()
