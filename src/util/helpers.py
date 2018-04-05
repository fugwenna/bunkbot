from pytz import timezone
from random import randint
from src.storage.db import database

RPG_CONSTANTS =  database.rpg.all()
XP_CONST: float = RPG_CONSTANTS[0]["xp_const"]
UPDATE_CAP: int = RPG_CONSTANTS[1]["update_cap"]
TIMER_MINUTES: int = RPG_CONSTANTS[2]["timer_minutes"]

EST = timezone("US/Eastern")

# calculate the required xp for a given level
def calc_req_xp(level: int) -> float:
    return (XP_CONST * level * level) - (XP_CONST * level) + round(level / 2, 2)

# roll a random value within a range
def roll(min_val: int = 0, max_val: int = 100) -> str:
    return str(randint(min_val, max_val))