from discord import Channel
from ..util.constants import CHANNEL_GENERAL
from ..models.service import Service
from ..bunkbot import BunkBot

"""
Service responsible for handling channel references
"""
class ChannelService(Service):
    def __init__(self, bot: BunkBot):
        super().__init__(bot)
        self.bot_testing: Channel = None

    # get an instance of a
    # channel based on the given name - if
    # no name is specified, the general chat is assumed
    async def get(self, name: str = CHANNEL_GENERAL) -> Channel:
        try:
            next(c for c in self.server.channels if c.name == name)
        except Exception:
            return
            # todo ...
