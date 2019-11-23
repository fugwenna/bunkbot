from ..bunkbot import BunkBot
from ..models.service import Service
from ..models.bunk_user import BunkUser
from ..services.database_service import DatabaseService

"""
Service responsible for handling any
bunk user references + syncing with database
"""
class UserService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService):
        super().__init__(bot)
        self.users: list = []
        self.bot.on_initialized += self.load_users
        self.database: DatabaseService = database

    # when the main bot is loaded, collect
    # members from the server and initialize
    # bunkuser instances for future use
    async def load_users(self) -> None:
        for member in self.server.members:
            # check the database if this user
            # has been added before collecting
            # a new instance of a bunk user
            db_user = self.database.get_user_by_member_ref(member)
            self.users.append(BunkUser(member, db_user))

        print(len(self.users))

    # retrieve a user based on the member
    # identifier
    def get_by_id(self, mid: int) -> BunkUser:
        return next(u for u in self.users if u.id == mid)