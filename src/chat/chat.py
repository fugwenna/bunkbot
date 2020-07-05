from discord import Message
from time import time
from re import findall, sub, IGNORECASE

from ..core.bunk_user import BunkUser
from ..core.functions import will_execute_on_chance

"""
This class represents a chat between
bunkbot and a bunk user
"""
class Chat:
    def __init__(self, user: BunkUser, message: Message):
        self.timer: int = 13
        self.last_message_at: int = time()
        self.user: BunkUser = user
        self.channel_id: int = message.channel.id
        self.content: str = Chat.parse_message(message.content)

    
    @property
    def is_active(self) -> bool:
        still_chatting = self.check_if_active()

        if still_chatting:
            self.last_message_at: int = time()

        return still_chatting

    
    def check_if_active(self) -> bool:
        new_time = time() - self.last_message_at
        still_chatting = new_time < self.timer

        if not still_chatting:
            self.last_message_at = -1

        return still_chatting


    def reply(self, message: str, user: BunkUser) -> None or str:
        if (user.id != self.user.id):
            respond: bool = will_execute_on_chance(85)

            if not respond:
                return

        self.last_message_at = time()

        return Chat.parse_message(message)

    
    @staticmethod
    def parse(content: str) -> list:
        return findall("[a-zA-Z]+", str(content).lower())


    @staticmethod
    def parse_message(content: str) -> str:
        return sub(r'bunkbot', "", str(content), flags=IGNORECASE).strip()