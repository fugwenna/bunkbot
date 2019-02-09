from src.bunkbot import BunkBot
from src.models.service import Service
from src.services.database_service import DatabaseService

"""
Service responsible for anything superuser
related - handles some logic for admin/moderator cogs
"""
class SudoService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService):
        super().__init__(bot, database)
        self.SERVER_LOCKED: bool = False