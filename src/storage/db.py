"""
Wrapper for the TinyDB database storage
with helper methods and additional functions
"""
import discord, time, datetime, pytz
from tinydb import TinyDB, Query
from tinydb.database import Table
from ..cogs.rpg import rpg

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


    # get a user based on the passed
    # discord member reference
    def get_user(self, member: discord.Member) -> any:
        return self.users.get(Query().name == member.name)


    # save an updated user reference
    # and return the updated user
    def save_user(self, user: any, query: any) -> None:
        self.users.update(query, Query().name == user.name)
        return self.get_user(user.name)


    # check if a user exists in the database - if not,
    # add them with base roles and properties
    def check_user(self, member: discord.Member) -> bool:
        user: Table = self.users.search(Query().name == member.name)

        if len(user) == 0:
            self.users.insert({"name": member.name, "xp": 0, "level": 1})
            if not str(member.status) == "offline":
                self.update_user_last_online(member)
            return True

        if not str(member.status) == "offline":
            self.update_user_last_online(member)
        return False


    # update the "last online" property for
    # a user when a user appears online
    def update_user_last_online(self, member: discord.Member) -> None:
        now = datetime.datetime.now(tz=pytz.timezone("US/Eastern"))
        last_on = "{0:%m/%d/%Y %I:%M:%S %p}".format(now)
        self.users.update({"last_online": last_on}, Query().name == member.name)


    # update the users level percentage
    # and return the user reference
    def update_user_xp(self, member: discord.Member, value: float) -> any:
        user = self.get_user(member)
        cur_pct = float(user["xp"])

        self.users.update({"xp": cur_pct + value}, Query().name == member.name)

        user = self.get_user(member)
        return user


    # update the users level
    # and return the user reference
    def update_user_level(self, member: discord.Member) -> any:
        user = self.get_user(member)
        cur_lvl = int(user["level"])

        self.users.update({"level": cur_lvl + 1}, Query().name == member.name)

        user = self.get_user(member)
        return user


database = BunkDB()