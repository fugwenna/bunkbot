from discord.ext.commands import command, Context, Cog
from ..core.registry import TIME_SERVICE
from ..bunkbot import BunkBot
from .time_service import TimeService


TIME_DESCRIPTION: str = """There is literally no reason for this cog"""


class Time(Cog):
    def __init__(self, time: TimeService):
        self.time: TimeService = time


    @command(help=TIME_DESCRIPTION)
    async def time(self, ctx: Context) -> None:
        await ctx.trigger_typing()
        time = await self.time.get_time(ctx.message)

        await ctx.send(time)


def setup(bot: BunkBot) -> None:
    bot.add_cog(Time(TIME_SERVICE))
