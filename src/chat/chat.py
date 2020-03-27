from time import time
from re import findall, sub, IGNORECASE

from ..core.bunk_user import BunkUser
from ..core.functions import roll_int

"""
This class represents a chat between
bunkbot and a bunk user
"""
class Chat:
    def __init__(self, user: BunkUser, content: str):
        self.timer: int = 13
        self.last_message_at: int = time()
        self.user: BunkUser = user
        self.content: str = Chat.parse_message(content)

    
    @property
    def is_active(self) -> bool:
        new_time = time() - self.last_message_at
        still_chatting = new_time < self.timer


        if not still_chatting:
            self.last_message_at = -1
        else:
            self.last_message_at: int = time()

        return still_chatting


    def reply(self, message: str, user: BunkUser) -> None or str:
        if (user.id != self.user.id):
            respond: bool = roll_int(0, 100) > 30

            if not respond:
                return

        self.last_message_at = time()

        return Chat.parse_message(message)

    
    @staticmethod
    def parse(content: str) -> str:
        return findall("[a-zA-Z]+", str(content).upper())


    @staticmethod
    def parse_message(content: str) -> str:
        return sub(r'bunkbot', "", str(content), flags=IGNORECASE).strip()