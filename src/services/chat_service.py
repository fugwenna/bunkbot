from src.bunkbot import BunkBot
from src.models.service import Service
from src.services.database_service import DatabaseService

"""
Service responsible for dealing with
CleverBot and responding to
"""
class ChatService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService):
        super().__init__(bot, database)