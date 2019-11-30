from typing import List
from discord import Embed
from discord.ext.commands import command, Context

from ..bunkbot import BunkBot
from ..models.bunk_user import BunkUser
from ..services.channel_service import ChannelService
from ..services.registry import USER_SERVICE, CHANNEL_SERVICE
from ..services.user_service import UserService
from ..util.functions import get_cmd_params

ROLE_DESCRIPTION = """Roll a random value between 0 and 100.  Optionally, you may pass a value range.\n
    Example: !roll
    Example: !roll 1-10
"""
class Roll:
    def __init__(self, channels: ChannelService, users: UserService):
        self.channels: ChannelService = channels
        self.users: UserService = users


    # roll a random number
    # optionally specify a value range with default 0-100
    @command(help=ROLE_DESCRIPTION)
    async def roll(self, ctx: Context) -> None:
        try:
            await ctx.trigger_typing()

            min_val: int = 0
            max_val: int = 100
            params: List[str] = get_cmd_params(ctx)
            user: BunkUser = self.users.get(ctx.author.id)

            if len(params) > 0:
                if "-" in params[0]:
                    p_split: str = params[0].split("-")
                    if p_split[0].isdigit() and p_split[1].isdigit():
                        val_1 = int(p_split[0])
                        val_2 = int(p_split[1])
                        min_val: int = val_1 if val_1 <= val_2 else val_2
                        max_val: int = val_1 if val_2 <= val_1 else val_2

            title: str = "Rolling ({0}-{1})".format(min_val, max_val)
            message: str = "{0} rolls {1}".format(user.name, str(randint(min_val, max_val)))

            await ctx.send(embed=Embed(title=title, description=message, color=ctx.author.color))
        except Exception as e:
            await self.channels.log_error(e, "roll")


def setup(bot: BunkBot) -> None:
    bot.add_cog(Roll(CHANNEL_SERVICE, USER_SERVICE))
