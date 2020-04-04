from discord import TextChannel, Message, Embed
from discord.ext.commands import Context

from ..bunkbot import BunkBot
from ..core.constants import CHANNEL_GENERAL, CHANNEL_BOT_LOGS, CHANNEL_BOT_TESTING, CHANNEL_USERS, CHANNEL_MOD_CHAT
from ..core.error_log_service import ErrorLogService
from ..core.service import Service
from ..db.database_service import DatabaseService

INFO: str = ":information_source:"
EXCLAMATION: str = ":exclamation:"
ROBOT: str = ":robot:"

"""
Service responsible for handling channel references
"""
class ChannelService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService, logger: ErrorLogService):
        super().__init__(bot, database)
        self.BOT_TESTING: TextChannel = None
        self.BOT_LOGS: TextChannel = None
        self.USER_LOG: TextChannel = None
        self.GENERAL: TextChannel = None
        self.WEATHER: TextChannel = None
        self.MOD_CHAT: TextChannel = None
        self.logger: ErrorLogService = logger


    # locate specific channels setup through
    # user and code config
    async def load(self) -> None:
        await super().load()

        if self.server is not None: 
            self.BOT_LOGS = await self._get(CHANNEL_BOT_LOGS)
            self.BOT_TESTING = await self._get(CHANNEL_BOT_TESTING)
            self.USER_LOG = await self._get(CHANNEL_USERS)
            self.GENERAL = await self._get(CHANNEL_GENERAL)

            if self.BOT_LOGS is not None:
                await self.BOT_LOGS.purge()
                await self.BOT_LOGS.send("{0} Bot loaded {1}".format(ROBOT, ROBOT))
            else:
                self.logger.log_warning("Cannot locate bot logs channel for logging", "ChannelService")
        else:
            self.logger.log_warning("No channels could be loaded from a null server", "ChannelService")


    # log a simple information message to 
    # the bot logs channel
    async def log_info(self, message: str, channel: TextChannel = None) -> None:
        await self.log(message, channel, "INFO")


    async def log_warning(self, message: str, channel: TextChannel = None) -> None:
        await self.log(message, channel, "INFO")


    async def log(self, message: str, channel: TextChannel = None, msg_type: str = None) -> None:
        try:
            if channel is None:
                channel = self.BOT_LOGS

            if channel is None:
                self.logger.log(message, "ChannelService", msg_type)
            else:
                await channel.send("{0} {1}".format(INFO, message))
        except Exception as e:
            self.logger.log_error(e, "ChannelService")


    # log an error in the bot_logs channel when
    # BunkBot emits the error event
    async def log_error(self, error: Exception, command: str, ctx: Context = None) -> None:
        try:
            error_message: str = "{0} Error occurred from command '{1}': {2}".format(EXCLAMATION, command, error)

            if ctx is not None:
                msg: Message = ctx.message
                err: str = "{0} An error has occurred! {1} help ahhhh".format(EXCLAMATION, self.bot.ADMIN_USER.mention)
                await msg.channel.send(err)

            if self.BOT_LOGS is None:
                self.logger.log_error(error_message, "ChannelService")
            else:
                await self.BOT_LOGS.send(error_message)
        except Exception as e:
            self.logger.log_error(e, "ChannelService")


    # send the 'typing' event to a channel based on a context message
    async def start_typing(self, ctx: Context) -> None:
        await ctx.trigger_typing()


    # get an instance of a
    # channel based on the given name - if
    # no name is specified, the general chat is assumed
    async def _get(self, name: str) -> TextChannel:
        return next((c for c in self.server.channels if c.name == name), None)