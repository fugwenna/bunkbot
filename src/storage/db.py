"""
Wrapper for the TinyDB database storage
with helper methods and additional functions
"""
from tinydb import TinyDB, Query

class BunkDB:
    # establish a 'connection' to the local
    # database and read in the primary tables
    def __init__(self):
        self.db = TinyDB("db.json")
        self.config = self.db.table("config")
        self.cogs = self.db.table("cogs")
        self.users = self.db.table("users")


database = BunkDB()