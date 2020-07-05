import datetime as dt
from discord.ext.commands import Context
from re import sub
from random import randint

from .constants import USER_NAME_REGEX

"""
Remove bad characters that aren't allowed 
in the 'username' regex (non alphanumeric)
"""
def simple_string(name: str, to_lower: bool = True) -> str:
    if name is None:
        name = ""

    new_name: str = sub(USER_NAME_REGEX, "", name.lower()).strip()

    if to_lower:
        return new_name.lower()
    else:
        return new_name


"""
Given a discord context, parse the message and
retrieve the parameters specified to the command
"""
def get_cmd_params(ctx: Context) -> list:
    if ctx is not None:
        return ctx.message.content.split()[1:]
    else:
        return []


def will_execute_on_chance(chance: int) -> bool:
    return randint(1, 100) <= chance

