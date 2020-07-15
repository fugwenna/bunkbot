from typing import List
from random import randint
from discord.ext.commands import Context

from ..core.http import http_get
from ..core.functions import get_cmd_params


XKCD_BASE_URL: str = "https://xkcd.com"
XKCD_INFO_URL: str = "https://xkcd.com/info.0.json"
XKCD_JSON_URL: str = "https://xkcd.com/{0}/info.0.json"


async def get_xkcd_comic(ctx: Context) -> any:
    p_comic: int = None
    latest: dict = await http_get(XKCD_INFO_URL)

    params: List[str] = get_cmd_params(ctx)
    if len(params) > 0:
        p_flag = params[0]
        if p_flag.isdigit() and int(p_flag) <= latest["num"]:
            p_comic = p_flag

    if p_comic is not None:
        return await http_get(XKCD_JSON_URL.format(p_comic))

    return await http_get(XKCD_INFO_URL)
