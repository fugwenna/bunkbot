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