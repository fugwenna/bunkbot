from discord.ext.commands import Context
from re import sub
from random import randint

from .constants import USER_NAME_REGEX

"""
Remove bad characters that aren't allowed 
in the 'username' regex (non alphanumeric)
"""
def simple_string(name: str) -> str:
    if name is None:
        name = ""

    new_name: str = sub(USER_NAME_REGEX, "", name.lower()).strip()

    return new_name.lower()


"""
Given a discord context, parse the message and
retrieve the parameters specified to the command
"""
def get_cmd_params(ctx: Context) -> list:
    if ctx is not None:
        return ctx.message.content.split()[1:]
    else:
        return []


# roll a random value within a range
def roll_int(min_val: int = 0, max_val: int = 100) -> int:
    return randint(min_val, max_val)