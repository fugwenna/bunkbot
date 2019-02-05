from discord import Server
from src.db.db import database
from src.util.constants import DB_SERVER_ID
from src.bunkbot import BunkBot

"""
Base class which all services should extend - this will
hold base information for BunkBot - server ref, database ref, etc
"""
class Service:
    def __init__(self, bot: BunkBot):
        self.database = database
        self.bot: BunkBot = bot
        self.server: Server = None
        bot.on_initialized += self.load

    # When bunkbot is loaded, all services
    # will load the server instance and other
    # default utils
    async def load(self) -> None:
        self.server = self.bot.get_server(self.database.get(DB_SERVER_ID))