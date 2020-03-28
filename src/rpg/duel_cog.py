from typing import List
from discord.ext.commands import command, Context, Cog

from ..bunkbot import BunkBot
from ..core.bunk_exception import BunkException
from ..core.bunk_user import BunkUser
from ..core.registry import RPG_SERVICE
from .duel import Duel
from .duel_result import DuelResult
from .rpg_service import RpgService


ALIASES: List[str] = ["challenge", "fight", "smack"]

DUEL_DESCRIPTION: str = """Challenge another user to a duel!
ex: !duel fugwenna
"""
class DuelCog(Cog):
    def __init__(self, rpg: RpgService):
        self.rpg: RpgService = rpg


    @command(help=DUEL_DESCRIPTION, aliases=ALIASES)
    async def duel(self, ctx: Context) -> None:
        try:
            duel: Duel = await self.rpg.challenge_duel(ctx)

            msg: str = """:triangular_flag_on_post: {0.mention} is challenging {1.mention} to a duel! 
            Type !accept to duel, or !reject to run away like a little biiiiiiiiiiiiitch""".format(duel.challenger, duel.opponent)

            await ctx.message.channel.send(msg)
        except BunkException as be:
            await ctx.message.channel.send(be.message)


    @command(help="Accept a duel")
    async def accept(self, ctx: Context) -> None:
        try:
            if self.rpg.accept_duel(ctx.message.author):
                pass
        except BunkException as be:
            await ctx.message.channel.send(be.message)


    @command(help="Reject a duel")
    async def reject(self, ctx: Context) -> None:
        try:
            if self.rpg.reject_duel(ctx.message.author):
                await self.bot.say(":exclamation: {0.mention} has rejected the duel".format(ctx.message.author))
        except BunkException as be:
            await ctx.message.channel.send(be.message)

    
def setup(bot: BunkBot) -> None:
    bot.add_cog(DuelCog(RPG_SERVICE))
