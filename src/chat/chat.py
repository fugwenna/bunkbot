from ..core.bunk_user import BunkUser

"""
This class represents a chat between
bunkbot and a bunk user
"""
class Chat:
    def __init__(self, user: BunkUser):
        self.timer: int = 0
        self.user: BunkUser = user

    # Reply to a message from the bunk user
    def reply(self, message: str, user: BunkUser) -> None or str:
        if (user.id != self.user.id):
            return

        response: str = "'"

        return response