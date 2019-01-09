from tinydb import TinyDB, Query
from tinydb.database import Table
from ..util.constants import \
    DB_PATH, DB_CONFIG, DB_USERS, DB_RPG, \
    DB_HOLIDAYS, DB_STREAMS, DB_GAMES

CONFIG = Query()

"""
Each service will get a reference to the static
bunk database instance - this is a TinyDB wrapper for
getting things like tokens, configs, etc
"""
class BunkDatabase:
    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.config: Table = self.db.table(DB_CONFIG)
        self.users: Table = self.db.table(DB_USERS)
        self.rpg: Table = self.db.table(DB_RPG)
        self.holidays: Table = self.db.table(DB_HOLIDAYS)
        self.streams: Table = self.db.table(DB_STREAMS)
        self.game_names: Table = self.db.table(DB_GAMES)

    # helper method that will query the requested table
    # and property name - default table as config
    def get(self, attr: str) -> str or None:
        res = self.config.get(CONFIG[attr] != "")
        if res is not None:
            return res[attr]
        else:
            return None


database = BunkDatabase()