from discord import Member
from ..models.service import Service
from ..bunkbot import BunkBot

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
        pass