from ..models.service import Service
from ..bunkbot import BunkBot

"""
Service responsible for dealing with
CleverBot and responding to
"""
class ChatService(Service):
    def __init__(self, bot: BunkBot):
        super().__init__(bot)