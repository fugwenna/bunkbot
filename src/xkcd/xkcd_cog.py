from discord.ext.commands import command, Context, Cog

from .xkcd_service import XKCDService
from ..bunkbot import BunkBot
from ..core.registry import XKCD_SERVICE


XKCD_DESCRIPTION: str = "Get a random XKCD comic or specify the comic number"

class XKCDCog(Cog):
    def __init__(self, xkcd: XKCDService):
        self.xkcd_svc: XKCDService = xkcd


    @command(description=XKCD_DESCRIPTION, aliases=["x"])
    async def xkcd(self, ctx: Context) -> None:
        """
        Fetch an XKCD comic and allow the user to
        either get a random one (no params) or specify
        a number

        Parameters 
        -----------
        ctx: Context
            Discord context which to pass to the service to fetch a comic
        """
        try:
            result: dict = await self.xkcd_svc.get_xkcd_comic(ctx)
            embed = self.xkcd_svc.create_embed_comic(result)

            await ctx.send(embed=embed)
        except Exception as ex:
            print(ex)

    
def setup(bot: BunkBot) -> None:
    bot.add_cog(XKCDCog(XKCD_SERVICE))
