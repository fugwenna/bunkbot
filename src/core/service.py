from discord import Guild

from .constants import DB_SERVER_ID
from ..bunkbot import BunkBot
from ..db.database_service import DatabaseService

"""
Base class which all services should extend - this will
hold base information for BunkBot - server ref, database ref, etc
"""
class Service:
    def __init__(self, bot: BunkBot, database: DatabaseService = None):
        self.database: DatabaseService = database
        self.bot: BunkBot = bot
        self.server: Guild = None
        bot.on_initialized += self.load

    # When bunkbot is loaded, all services
    # will load the server instance and other
    # default utils
    async def load(self) -> None:
        if self.database:
            srv = self.database.get(DB_SERVER_ID, False)

            if srv:
                self.server = self.bot.get_guild(int(srv))

                if not self.bot.server:
                    self.bot.server = self.server