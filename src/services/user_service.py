from ..bunkbot import BunkBot
from ..models.service import Service
from ..models.bunk_user import BunkUser

"""
Service responsible for handling any
bunk user references + syncing with database
"""
class UserService(Service):
    def __init__(self, bot: BunkBot):
        super().__init__(bot)
        self.users: list = []
        self.bot.on_initialized += self.load_users

    # when the main bot is loaded, collect
    # members from the server and initialize
    # bunkuser instances for future use
    async def load_users(self) -> None:
        for member in self.server.members:
            # check the database if this user
            # has been added before collecting
            # a new instance of a bunk user
            self.users.append(BunkUser(member))

    # retrieve a user based on the member
    # identifier
    def get(self, mid: int) -> BunkUser:
        return next(u for u in self.users if u.id == mid)