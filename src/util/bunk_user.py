import datetime, pytz
from time import time
from discord import Member, Server, Channel
from src.storage.db import database
from src.cogs.rpg.duel import Duel
from src.util.helpers import TIMER_MINUTES, UPDATE_CAP, calc_req_xp
from src.util.functions import to_name
from src.util.event_hook import EventHook
from src.util.constants import *


"""
Wrapper for users that merge
discord.Member and database user
"""
class BunkUser:
    on_level_up = EventHook()

    def __init__(self, member: Member=None):
        now = datetime.datetime.now(tz=pytz.timezone("US/Eastern"))
        self.duel: Duel = None
        self.duel_roll = 0
        self.last_online = "{0:%m/%d/%Y %I:%M:%S %p}".format(now)
        self.xp_holder = 0.0
        self.xp_last_update = time()

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
                    m.name == ROLE_MODERATOR or
                    m.name == ROLE_MODERATOR_PERMS or
                    m.name == ROLE_ADMIN]) > 0


    # check if the current
    # user is a vip
    @property
    def is_vip(self) -> bool:
        if self.member is None:
            return False

        return len([m for m in self.member.roles if m.name == ROLE_VIP or m.name == ROLE_VIP_PERMS]) > 0


    # current database user last xp updated date
    @property
    def last_xp_updated(self) -> str or None:
        if self.member is None:
            return None

        db_user = database.get_user_by_id(self.id)

        try:
            return db_user["last_xp_updated"]
        except:
            return None


    # current database user xp
    @property
    def xp(self) -> float:
        if self.member is None:
            return 1

        db_user = database.get_user_by_id(self.id)
        return db_user["xp"]


    @property
    def level(self) -> int:
        if self.member is None:
            return 1

        db_user = database.get_user_by_id(self.id)
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


    # recursively check if the user
    # has leveled n levels
    @property
    def has_leveled_up(self) -> bool:
        leveled = False

        while self.xp > calc_req_xp(self.next_level):
            leveled = True
            self.from_database(database.update_user_level(self.id))

        return leveled


    # wrapper for checking
    # if the user is streaming
    @property
    def is_streaming(self) -> bool:
        if not self.member:
            return False

        return self.member.game is not None and self.member.game.type == 1


    # check if the member is
    # currently playing a game
    @property
    def is_gaming(self) -> bool:
        if not self.member:
            return False

        return self.member.game is not None and self.member.game.type == 0


    # id reference for hotslogs
    @property
    def hots_ref(self) -> int:
        return -1


    # check if the  bunk user
    # has a given role
    def has_role(self, role: str) -> bool:
        return len([r for r in self.member.roles if r.name == role]) > 0


    # update properties from a discord
    # member and remap with the database equivalent
    def from_server(self, member: Member) -> None:
        self.member = member
        self.id = self.member.id
        self.name = to_name(self.member.name)
        db_user = database.get_user_by_id(self.id)

        if db_user is not None:
            try:
                self.last_online = db_user["last_online"]
            except KeyError:
                pass #user never online
        else:
            print("User '{0}' not in database...".format(self.name))


    # update properties from a database user
    # and remap with the server equivalent
    def from_database(self, db_user: any, server: Server = None) -> None:
        self.last_online = db_user["last_online"]

        if server is not None:
            member_search = [m for m in server.members if m.name == db_user.id == m.id]
            if len(member_search) > 0:
                self.from_server(member_search[0])
        elif self.member is not None:
            self.from_server(self.member)


    # update the database user last
    # online property
    async def update_last_online(self):
        database.update_user_last_online(self.id)

        if self.xp_holder > 0:
            await self.update_xp(0, None, True)


    # update the bunk user xp
    # by a given value
    async def update_xp(self, value, channel: Channel = None, force = False) -> None:
        diff = time() - self.xp_last_update

        if force or diff > 0:
            min_diff = diff / 60

            # continue to increase the message
            # count until the user has reached a cap
            # during an n minute window
            if not force and min_diff <= TIMER_MINUTES:
                if self.xp_holder < UPDATE_CAP:
                    self.xp_holder += value

            # the window is up, therefore
            # increase the user level percentage and
            # check if they have leveled up
            elif force or min_diff > TIMER_MINUTES:
                self.from_database(database.update_user_xp(self.id, self.xp_holder))

                if self.has_leveled_up:
                    await BunkUser.on_level_up.fire(self.member, self.level, channel)

                self.xp_last_update = time()
                self.xp_holder = value
