from re import sub
from ..util.constants import USER_NAME_REGEX

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
Get a random number between a given range
"""
def get_random_number(min_val: int = 0, max_val: int = 100) -> int:

    return 0