"""
Wrapper for the TinyDB database storage
with helper methods and additional functions
"""
from tinydb import TinyDB, Query
from tinydb.database import Table

class BunkDB:
    # establish a 'connection' to the local
    # database and read in the primary tables
    def __init__(self):
        self.db = TinyDB("src/storage/db.json")
        self.config: Table = self.db.table("config")
        self.cogs: Table = self.db.table("cogs")
        self.users: Table = self.db.table("users")


    # helper method that will query the requested table
    # and property name - default table as config
    def get(self, attr: str, table: str = "config") -> str:
        q: Query = Query()
        tab: Table = self.db.table(table)
        res = tab.get(q[attr] != "")
        if res is not None:
            return res[attr]
        else:
            return None



database = BunkDB()