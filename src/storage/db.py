"""
Wrapper for the TinyDB database storage
with helper methods and additional functions
"""
import discord, datetime, pytz
from tinydb import TinyDB, Query
from tinydb.database import Table


class BunkDB:
    # establish a 'connection' to the local
    # database and read in the primary tables
    def __init__(self):
        self.db = TinyDB("src/storage/db.json")
        self.config: Table = self.db.table("config")
        self.users: Table = self.db.table("users")
        self.rpg: Table = self.db.table("rpg")
        self.check_defaults()


    # set default database and config values
    def check_defaults(self):
        if len(self.config.all()) == 0:
            self.config.insert_multiple([{"token": ""}, {"serverid": ""}, {"cleverbot": ""}, {"weather":""}])

        if len(self.rpg.all()) == 0:
            self.rpg.insert_multiple([{"xp_const": 5}, {"update_cap": 60}, {"timer_minutes": 1}])


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

    # get a user based on the passed
    # discord member reference
    def get_user2(self, name: str) -> any:
        return self.users.get(Query().name == name)


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
        cur_xp = float(user["xp"])

        new_xp = 0
        if cur_xp + value > 0:
            new_xp = round(cur_xp + value, 2)

        self.users.update({"xp": new_xp}, Query().name == member.name)

        user = self.get_user(member)
        return user


    # update the users level
    # and return the user reference
    def update_user_level(self, member: discord.Member, value: int = 1) -> any:
        user = self.get_user(member)
        cur_lvl = int(user["level"])

        self.users.update({"level": cur_lvl + value}, Query().name == member.name)

        user = self.get_user(member)
        return user


database: BunkDB = BunkDB()