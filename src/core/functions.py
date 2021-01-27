import datetime as dt
from typing import List
from discord.ext.commands import Context
from re import sub
from random import randint

from .constants import USER_NAME_REGEX

def simple_string(name: str, to_lower: bool = True) -> str:
    """
    Remove bad characters that aren't allowed 
    in the 'username' regex (non alphanumeric)

    Parameters
    -----------
    name: str
        Name of the string to format to a 'simple' format

    to_lower: bool (default True)
        Convert the case of the string to all lowercase

    Returns
    -------
    Formatted 'simple' string with no special characters
    """
    if name is None:
        name = ""

    new_name: str = sub(USER_NAME_REGEX, "", name.lower()).strip()

    if to_lower:
        return new_name.lower()
    else:
        return new_name


def get_cmd_params(ctx: Context) -> List[str]:
    """
    Given a discord context, parse the message and
    retrieve the parameters specified to the command

    Parameters
    -----------
    ctx: Context
        Discord context of an ext.command

    Returns
    --------
    A list of strings representing the command parameters
    """
    if ctx is not None:
        return ctx.message.content.split()[1:]
    else:
        return []


def will_execute_on_chance(chance: int) -> bool:
    return randint(1, 100) <= chance


def is_stupid_mkr(name: str) -> bool:
    """
    Stupid mkr

    Parameters
    -----------
    name: str
        Name of user, maybe stupid mkr
    """
    if name is None:
        return False

    return name.lower() == "mkr"
