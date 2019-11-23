from typing import List
from ..bunkbot import BunkBot
from ..models.service import Service
from ..models.chat_context import ChatContext
from ..services.database_service import DatabaseService

"""
Service responsible for dealing with
CleverBot and responding to
"""
class ChatService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService):
        super().__init__(bot, database)
        self.chats: List[ChatContext] = []