from discord.ext.commands import Context
from re import sub

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


def get_cmd_params(ctx: Context) -> list:
    if ctx is not None:
        return ctx.message.content.split()[1:]
    else:
        return []
