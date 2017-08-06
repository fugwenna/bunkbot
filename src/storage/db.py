"""
Wrapper for the TinyDB database storage
with helper methods and additional functions
"""
import discord, time, datetime, pytz
from tinydb import TinyDB, Query
from tinydb.database import Table

class BunkDB:
    # establish a 'connection' to the local
    # database and read in the primary tables
    def __init__(self):
        self.db = TinyDB("src/storage/db.json")
        self.config: Table = self.db.table("config")
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


    # check if a user exists in the database - if not,
    # add them with base roles and properties
    def check_user(self, member: discord.Member) -> bool:
        user: Table = self.users.search(Query().name == member.name)

        if len(user) == 0:
            self.users.insert({"name": member.name})
            if str(member.status) == "online":
                self.update_user_last_online(member)
            return True

        if str(member.status) == "online":
            self.update_user_last_online(member)
        return False


    # update the "last online" property for
    # a user when a user appears online
    def update_user_last_online(self, member: discord.Member) -> None:
        now = datetime.datetime.now(tz=pytz.timezone("US/Eastern"))
        last_on = "{0:%m/%d/%Y %I:%M:%S %p}".format(now)
        self.users.update({"last_online": last_on}, Query().name == member.name)


database = BunkDB()