from discord import TextChannel, CategoryChannel, Message, Embed
from discord.ext.commands import Context

from ..bunkbot import BunkBot
from ..core.service import Service
from ..channel.log_types import LOG_WARNING, LOG_INFO
from ..db.database_service import DatabaseService
from ..etc.config_service import ConfigService


INFO: str = ":information_source:"
EXCLAMATION: str = ":exclamation:"
ROBOT: str = ":robot:"


class ChannelService(Service):
    """
    Service responsible for handling channel references

    Parameters
    -----------
    bot: Bunkbot
        Super class instance of the bot

    database: DatabaseService
        Super class instance of the database service
    """
    def __init__(self, bot: BunkBot, database: DatabaseService):
        super().__init__(bot, database)
        self.config.raise_error_on_bad_config = False


    async def load(self) -> None:
        """
        @override

        On load (event), send a log to the configured log
        channel that the bot has successfully loaded
        """
        await super().load()

        if self.server is not None: 
            log_channel: TextChannel = await self.get_by_name(self.config.log_channel)

            if log_channel is not None:
                await log_channel.purge()
                await log_channel.send("{0} Bot loaded {1}".format(ROBOT, ROBOT))
            else:
                self.logger.log_warning("Cannot locate bot logs channel for logging", "ChannelService")
                self.logger.log_info("Bot loaded", "ChannelService")
        else:
            self.logger.log_warning("No channels could be loaded from a null server", "ChannelService")


    async def send_to_primary_channel(self, message: str) -> None:
        """
        Send a message to the configured "primary" channel (i.e. general)
        If the channel cannot be found, send a warning to either the text log
        or configured log channel

        Parameters
        -----------
        message: str
            The string content of a message to send
        """
        channel: TextChannel = await self.get_by_name(self.config.primary_channel)
        if channel is not None:
            await channel.trigger_typing()
            await channel.send(message)
        else:
            await self.log_warning("Unknown primary channel", "ChannelService")
            await self.log_info(message, "ChannelService")


    async def log_info(self, message: str, channel: TextChannel = None) -> None:
        """
        'Information' log - add a basic log to a given channel 

        Parameters
        -----------
        message: str
            Message to send to the given channel

        channel: TextChannel (optional)
            Channel which to send (default to configured log channel)
        """
        await self._log(message, channel, LOG_INFO)


    async def log_warning(self, message: str, channel: TextChannel = None) -> None:
        """
        'Warning' log - add a basic log to a given channel 

        Parameters
        -----------
        message: str
            Message to send to the given channel

        channel: TextChannel (optional)
            Channel which to send (default to configured log channel)
        """
        await self._log(message, channel, LOG_WARNING)


    async def log_error(self, error: Exception, command: str, ctx: Context = None) -> None:
        """
        'Error' log - send an error to either the channel from the discord contents or log channel

        Parameters
        -----------
        error: Exception
            The error that has been thrown

        command: str
            The command from which the error was thrown

        ctx: Context (optional)
            The discord context the original command was executed
        """
        try:
            error_message: str = "{0} Error occurred from command '{1}': {2}".format(EXCLAMATION, command, error)

            if ctx is not None:
                err: str = "{0} An error has occurred! {1} help ahhhh".format(EXCLAMATION, self.bot.ADMIN_USER.mention)
                await ctx.send(err)

            log_channel: TextChannel = await self.get_by_name(self.config.log_channel)
            if log_channel is None:
                self.logger.log_error(error_message, "ChannelService")
            else:
                await log_channel.send(error_message)
        except Exception as e:
            self.logger.log_error(e, "ChannelService")


    async def get_by_name(self, name: str) -> TextChannel:
        """ 
        Get an instance of a
        channel based on the given name - if
        no name is specified, the general chat is assumed

        Parameters
        -----------
        name: str
            Name of the channel which to find

        Returns
        --------
        Text channel found by name
        """
        if not self.server or not self.server.channels:
            return None

        return next((c for c in self.server.channels if c.name.lower() == name.lower()), None)


    async def _log(self, message: str, channel: TextChannel = None, msg_type: str = None) -> None:
        try:
            if channel is None:
                channel = await self.get_by_name(self.config.log_channel)

            if channel is None:
                if msg_type == LOG_WARNING:
                    self.logger.log_warning(message, "ChannelService")
                else:
                    self.logger.log_info(message, "ChannelService", msg_type)
            else:
                await channel.send("{0} {1}".format(INFO, message))
        except Exception as e:
            self.logger.log_error(e, "ChannelService")
