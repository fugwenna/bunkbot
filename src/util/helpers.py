from random import randint
from tinydb import Query
from src.storage.db import database

# calculate the required xp for a given level
def calc_req_xp(level: int) -> float:
    const = database.rpg.get(Query().xp_const > 0)["xp_const"]
    return (const * level * level) - (const * level) + level

# roll a random value within a range
def roll(min_val: int = 0, max_val: int = 100) -> str:
    return str(randint(min_val, max_val))