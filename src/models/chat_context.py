from .bunk_user import BunkUser

"""
This class represents a chat between
bunkbot and a bunk user
"""
class ChatContext:
    def __init__(self, user: BunkUser):
        self.timer = 0
        self.user: BunkUser = user

    # Reply to a message from the bunk user
    def reply(self, message: str, user: BunkUser) -> None|str:
        if (user.id != self.user.id):
            return

        response: str = "'"

        return response