from discord import Channel
from ..bunkbot import BunkBot
from ..models.service import Service
from ..util.constants import \
    CHANNEL_GENERAL, CHANNEL_BOT_LOGS, CHANNEL_BOT_TESTING


"""
Service responsible for handling channel references
"""
class ChannelService(Service):
    def __init__(self, bot: BunkBot):
        super().__init__(bot)
        self.BOT_TESTING: Channel = None
        self.BOT_LOGS: Channel = None

    # locate specific channels setup through
    # user and code config
    async def load(self) -> None:
        await super().load()
        self.BOT_LOGS = await self.get(CHANNEL_BOT_LOGS)
        self.BOT_TESTING = await self.get(CHANNEL_BOT_TESTING)
        await self.bot.send_message(self.BOT_LOGS, "Bot loaded")

    # get an instance of a
    # channel based on the given name - if
    # no name is specified, the general chat is assumed
    async def get(self, name: str = CHANNEL_GENERAL) -> Channel:
        return next(iter(c for c in self.server.channels if c.name == name))
