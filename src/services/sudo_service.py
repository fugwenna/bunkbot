from discord import Member

from .database_service import DatabaseService
from .channel_service import ChannelService
from ..bunkbot import BunkBot
from ..models.service import Service
from ..util.constants import ROLE_MODERATOR

"""
Service responsible for anything superuser
related - handles some logic for admin/moderator cogs
"""
class SudoService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService, channels: ChannelService):
        super().__init__(bot, database)
        self.SERVER_LOCKED: bool = False # todo - not really used for anything, placeholder
        self.channels: ChannelService = channels
        self.bot.on_user_remove += self.handle_user_removal

    # inform moderators when users are removed from the server
    async def handle_user_removal(self, member: Member) -> None:
        channel = self.channels.MOD_CHAT
        msg = "@{0} :skull_crossbones: User '{1}' has left the server :skull_crossbones:".format(ROLE_MODERATOR, member.name)
        await self.bot.say_to_channel(channel, msg)