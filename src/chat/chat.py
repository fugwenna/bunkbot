from time import time

from ..core.bunk_user import BunkUser

"""
This class represents a chat between
bunkbot and a bunk user
"""
class Chat:
    def __init__(self, user: BunkUser):
        self.timer: int = 0
        self.last_message_at: int = -1
        self.user: BunkUser = user

    
    @property
    def is_active(self) -> bool:
        new_time = time() - self.last_message_at
        still_chatting = new_time < self.chat_timer

        if not still_chatting:
            self.last_message_at = -1

        return still_chatting


    # Reply to a message from the bunk user
    def reply(self, message: str, user: BunkUser) -> None or str:
        if (user.id != self.user.id):
            return

        response: str = "'"

        self.last_message_at = time()

        return response
