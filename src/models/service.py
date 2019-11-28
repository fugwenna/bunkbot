from discord import Server

from ..bunkbot import BunkBot
from ..services.database_service import DatabaseService
from ..util.constants import DB_SERVER_ID

"""
Base class which all services should extend - this will
hold base information for BunkBot - server ref, database ref, etc
"""
class Service:
    def __init__(self, bot: BunkBot, database: DatabaseService = None):
        self.database: DatabaseService = database
        self.bot: BunkBot = bot
        self.server: Server = None
        bot.on_initialized += self.load

    # When bunkbot is loaded, all services
    # will load the server instance and other
    # default utils
    async def load(self) -> None:
        if self.database:
            self.server = self.bot.get_server(self.database.get(DB_SERVER_ID))
