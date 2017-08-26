"""
Wrapper for users that merge
discord.Member and database user
"""
import datetime, pytz
from re import sub
from src.util.helpers import *
from discord import Member, Server
from src.storage.db import database
from src.util.helpers import USER_NAME_REGEX
from src.util.event_hook import EventHook


class BunkUser:
    def __init__(self, member: Member=None):
        now = datetime.datetime.now(tz=pytz.timezone("US/Eastern"))
        self.last_online = "{0:%m/%d/%Y %I:%M:%S %p}".format(now)
        self.xp_holder = 0.0
        self.is_dueling = False
        self.on_xp_gain = EventHook()
        self.on_xp_loss = EventHook()
        self.on_level_up = EventHook()
        self.on_level_down = EventHook()

        self.member: Member = None
        self.id = -1
        self.name = ""

        if member is not None:
            self.from_server(member)


    # check if the current
    # user is a moderator
    @property
    def is_moderator(self) -> bool:
        if self.member is None:
            return False

        return len([m for m in self.member.roles if
                    m.name == "moderator" or
                    m.name == "moderator_perms" or
                    m.name == "admin"]) > 0


    # check if the current
    # user is a vip
    @property
    def is_vip(self) -> bool:
        if self.member is None:
            return False

        return len([m for m in self.member.roles if m.name == "vip" or m.name == "vip_perms"]) > 0


    # current database user xp
    @property
    def xp(self) -> float:
        if self.member is None:
            return 1

        db_user = database.get_user2(self.member.name)
        return db_user["xp"]


    @property
    def level(self) -> int:
        if self.member is None:
            return 1

        db_user = database.get_user2(self.member.name)
        return db_user["level"]


    # next level value
    @property
    def next_level(self) -> int:
        return self.level + 1


    # previous level value
    @property
    def previous_level(self) -> int:
        return self.level - 1


    # wrap the mention property
    @property
    def mention(self) -> str:
        if self.member is None:
            return ""

        return self.member.mention


    # wrap the user roles
    @property
    def roles(self) -> list:
        if self.member is None:
            return []

        return self.member.roles


    # get the users color_
    # role if it is set
    @property
    def color(self) -> str or None:
        if self.color_role is None:
            return None

        return self.color_role.name.split("-")[1].lower()


    # return the color role
    # including the 'color_' prefix
    @property
    def color_role(self) -> str or None:
        if self.member is None:
            return None

        colors = [r for r in self.member.roles if "color-" in r.name.lower()]

        if len(colors) > 0:
            return colors[0]

        return None


    # update properties from a discord
    # member and remap with the database equivalent
    def from_server(self, member: Member) -> None:
        self.member = member
        self.id = self.member.id
        self.name = sub(USER_NAME_REGEX, "", self.member.name.lower())

        db_user = database.get_user2(member.name)
        if db_user is not None:
            self.xp_holder = db_user["xp"]
            try:
                self.last_online = db_user["last_online"]
            except KeyError:
                pass #user never online
        else:
            print("User '{0}' not in database...", self.name)


    # update properties from a database user
    # and remap with the server equivalent
    def from_database(self, db_user: any, server: Server = None) -> None:
        self.xp_holder = db_user["xp"]
        self.last_online = db_user["last_online"]

        if server is not None:
            member_search = [m for m in server if m.name == db_user["name"]]
            if len(member_search) > 0:
                self.from_server(member_search[0])
        elif self.member is not None:
            self.from_server(self.member)


    # update the bunk user xp
    # by a given value
    # todo - from database
    async def update_xp(self, value) -> None:
        req_xp = calc_req_xp(self.next_level)
        #print(req_xp)