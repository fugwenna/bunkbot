from src.bunkbot import BunkBot
from src.models.service import Service
from src.services.database_service import DatabaseService
from src.services.channel_service import ChannelService

"""
Service specifically designed to deal with things like
setting BunkBot's played game, twitch streams, etc.
"""
class GameService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService, channels: ChannelService):
        super().__init__(bot, database)
        self.channels: ChannelService = channels
        self.bot.on_initialized += self.wire_game
        self.bot.on_initialized += self.check_streams

    # when the bot has loaded, wire a listener which will setup
    # a random game that bunkbot is "playing"
    async def wire_game(self) -> None:
        pass

    # do an initial check of current streams and update
    # the list in the stream channel
    async def check_streams(self) -> None:
        pass