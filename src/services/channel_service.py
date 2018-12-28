from discord import Channel
from ..util.constants import CHANNEL_GENERAL
from ..models.service import Service

"""
Service responsible for handling channel references
"""
class ChannelService(Service):
    def __init__(self):
        super().__init__()
        self.bot_testing: Channel = None

    # get an instance of a
    # channel based on the given name - if
    # no name is specified, the general chat is assumed
    async def get(self, name: str = CHANNEL_GENERAL) -> Channel:
        try:
            return [
                ch for ch in self.server.channels if ch.ame == name
            ][0]
        except Exception:
            return
            # todo ...
