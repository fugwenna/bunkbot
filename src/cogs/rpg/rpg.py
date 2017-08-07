"""
Base RPG class used for leveling users
"""
import time
from discord import Member
from src.storage.db import database
from src.util.event_hook import EventHook


# hard cap the message
# processing to a discrete value
# to prevent channel spamming
UPDATE_CAP = 150
TIMER_MINUTES = 15
LEVEL_1 = 10
LEVEL_2 = 100
LEVEL_3 = 500


# calculate the percentage required
# to advance to the next level
# todo - dynamic calculation of next lvl pct
def calculate_level_pct(level: int) -> int:
    if level == 0:
        return LEVEL_1
    elif level == 1:
        return LEVEL_2
    else:
        return LEVEL_3

    #return LEVEL_BASE


class RPG:
    def __init__(self):
        self.config = {}
        self.on_user_level = EventHook()


    # sync a users level with the
    # config if they log on or off
    async def sync_user_level(self, member: Member) -> None:
        try:
            user = self.config[member.name]
            new_user = database.update_user_level_pct(member, user["value"])

            if new_user["level_pct"] >= calculate_level_pct(new_user["level"]):
                database.update_user_level(member)

                if str(member.status) == "online":
                    leveled_user = database.update_user_level(member)
                    await self.on_user_level.fire(member, leveled_user["level"])
        except:
            # no user to sync - just logged on
            pass



    # every time a user sends a message
    # process it for "leveling" logic
    async def update_user_level(self, member: Member, value: float) -> None:
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
            # during a 30 minute window
            if min_diff <= TIMER_MINUTES:
                if user["value"] < UPDATE_CAP:
                    user["value"] += value

            # the 30 minute window is up, therefore
            # increase the user level percentage and
            # check if they have leveled up
            else:
                new_user = database.update_user_level_pct(member, user["value"])

                if new_user["level_pct"] >= calculate_level_pct(new_user["level"]):
                    leveled_user = database.update_user_level(member)
                    await self.on_user_level.fire(member, leveled_user["level"])

                user["last_update"] = time.time()
                user["value"] = value


        #print(user)


rpg = RPG()