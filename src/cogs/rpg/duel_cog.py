from typing import List
from discord.ext.commands import command, Context, Cog

from ...bunkbot import BunkBot
from ...services.channel_service import ChannelService
from ...services.registry import USER_SERVICE, CHANNEL_SERVICE
from ...services.user_service import UserService

ALIASES: List[str] = ["challenge", "fight", "smack"]

def check(ctx: Context) -> bool:
    return False

DUEL_DESCRIPTION: str = """Challenge another user to a duel!

ex: !duel fugwenna
"""
class DuelCog(Cog):
    def __init__(self, users: UserService, channels: ChannelService):
        self.users: UserService = users
        self.channels: ChannelService = channels


    # duel another user in the server
    @command(help=DUEL_DESCRIPTION, aliases=ALIASES)#, checks=[check])
    async def duel(self, ctx: Context) -> None:
        await ctx.message.channel.send("Not yet implemented! (I am in rewrite mode)")


def setup(bot: BunkBot) -> None:
    bot.add_cog(DuelCog(USER_SERVICE, CHANNEL_SERVICE))
