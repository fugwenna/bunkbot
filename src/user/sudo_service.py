from discord import Member

from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.constants import ROLE_MODERATOR
from ..core.service import Service
from ..db.database_service import DatabaseService

"""
Service responsible for anything superuser
related - handles some logic for admin/moderator cogs
"""
class SudoService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService, channels: ChannelService):
        super().__init__(bot, database)
        self.SERVER_LOCKED: bool = False # todo - not really used for anything, placeholder
        self.channels: ChannelService = channels