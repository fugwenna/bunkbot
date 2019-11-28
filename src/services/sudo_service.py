from .database_service import DatabaseService
from ..bunkbot import BunkBot
from ..models.service import Service

"""
Service responsible for anything superuser
related - handles some logic for admin/moderator cogs
"""
class SudoService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService):
        super().__init__(bot, database)
        self.SERVER_LOCKED: bool = False