"""
Base RPG class used for leveling users
"""
import time
from discord import Member
from src.util.bunk_user import BunkUser
from src.storage.db import database
from src.util.helpers import  TIMER_MINUTES, UPDATE_CAP, XP_CONST
from src.util.event_hook import EventHook

class RPG:
    def __init__(self):
        self.config = {}
        self.on_user_level_up = EventHook()


    # sync a users level with the
    # config if they log on or off
    async def sync_user_xp(self, member: Member) -> None:
        new_user = None

            #user = self.config[member.name]
            #new_user = database.update_user_xp(member, user["value"])

            #if new_user is None:
            #    new_user = database.get_user(member.name)

            #if new_user is not None:
            #    pass
        #        if str(member.status) == "online" and self.level_up(new_user["xp"], new_user["level"] + 1):
        #            database.update_user_level(member)

        #            if str(member.status) == "online":
        #                leveled_user = database.update_user_level(member)
        #                await self.on_user_level_up.fire(member, leveled_user["level"])


    # every time a user sends a message
    # process it for "leveling" logic
    # todo - dep, rm
    async def update_user_xp(self, member: Member, value: float) -> None:
        try:
            user = self.config[member.name]
        except:
            self.config[member.name] = {"value": value, "last_update": time.time()}
            user = self.config[member.name]

        diff = time.time() - user["last_update"]

        if diff > 0:
            min_diff = diff / 60

            # continue to increase the message
            # count until the user has reached a cap
            # during an n minute window
            if min_diff <= TIMER_MINUTES:
                if user["value"] < UPDATE_CAP:
                    user["value"] += value

            # the window is up, therefore
            # increase the user level percentage and
            # check if they have leveled up
            else:
                new_user = database.update_user_xp(member, user["value"])

                if self.level_up(new_user["xp"], new_user["level"] + 1):
                    leveled_user = database.update_user_level(member)
                    await self.on_user_level_up.fire(member, leveled_user["level"])

                user["last_update"] = time.time()
                user["value"] = value


     # every time a user sends a message
     # process it for "leveling" logic
    async def update_user_xp_force(self, member: BunkUser, value: float) -> None:
        try:
            user = self.config[member.name]
        except:
            self.config[member.name] = {"value": value, "last_update": time.time()}
            user = self.config[member.name]

        new_user = database.update_user_xp(member.member, user["value"] + value)

        if self.level_up(new_user["xp"], new_user["level"] + 1):
            leveled_user = database.update_user_level(member)
            await self.on_user_level_up.fire(member, leveled_user["level"])

        user["last_update"] = time.time()
        return


    # calculate the required xp for a given level
    @staticmethod
    def calc_req_xp(level: int) -> float:
        return (XP_CONST * level * level) - (XP_CONST * level) + round(level / 2, 2)


    # calculate the xp required
    # to advance to the next level
    def level_up(self, xp: float, level: int) -> bool:
        return xp >= self.calc_req_xp(level)

rpg = RPG()
