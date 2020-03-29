from typing import List
from discord import Embed
from discord.ext.commands import command, Context, Cog

from ..bunkbot import BunkBot
from ..core.bunk_exception import BunkException
from ..core.bunk_user import BunkUser
from ..core.registry import RPG_SERVICE
from .duel import Duel
from .duel_result import DuelResult
from .rpg_service import RpgService


ALIASES: List[str] = ["challenge", "fight", "smack", "slap"]

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

            await ctx.send(msg)
        except BunkException as be:
            await ctx.send(be.message)


    @command(help="Accept a duel")
    async def accept(self, ctx: Context) -> None:
        try:
            usr: BunkUser = self.rpg.users.get_by_id(ctx.message.author.id)
            result: DuelResult = self.rpg.accept_duel(usr)

            embed = Embed(title=":crossed_swords: {0} vs {1}".format(result.challenger.name, result.opponent.name), color=int("FF0000", 16))
            embed.add_field(name="Name", value="\n".join([result.challenger.name, result.opponent.name]), inline=True)
            embed.add_field(name="Damage",
                            value="\n".join([str(result.challenger_roll), str(result.opponent_roll)]),
                            inline=True)

            await ctx.send(embed=embed)
            await ctx.send("{0} has bested {1} in a duel!".format(result.winner.mention, result.loser.name))

        except BunkException as be:
            await ctx.send(be.message)


    @command(help="Reject a duel")
    async def reject(self, ctx: Context) -> None:
        try:
            usr: BunkUser = self.rpg.users.get_by_id(ctx.message.author.id)
            if self.rpg.reject_duel(usr):
                await ctx.send(":exclamation: {0.mention} has rejected the duel".format(ctx.message.author))
        except BunkException as be:
            await ctx.send(be.message)

    
def setup(bot: BunkBot) -> None:
    bot.add_cog(DuelCog(RPG_SERVICE))
