from ..bunkbot import BunkBot
from ..models.service import Service
from ..services.database_service import DatabaseService

"""
Service responsible for dealing with
CleverBot and responding to
"""
class ChatService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService):
        super().__init__(bot, database)