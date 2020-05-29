from discord import Embed
from discord.ext.commands import command, Context, Cog

from .xkcd_comic_service import get_xkcd_comic
from ..bunkbot import BunkBot


XKCD_DESCRIPTION: str = "Get a random XKCD comic or specify the comic number"

class XKCDCog(Cog):
    # fetch an XKCD comic and allow the user to
    # either get a random one (no params) or specify
    # a number
    @command(description=XKCD_DESCRIPTION, aliases=["x"])
    async def xkcd(self, ctx: Context) -> None:
        try:
            result: dict = await get_xkcd_comic(ctx)

            embed: Embed = Embed()
            embed.title = result["safe_title"]
            embed.set_image(url=result["img"])
            embed.set_footer(text=result["alt"])

            await ctx.send(embed=embed)
        except Exception as ex:
            print(ex)

    
def setup(bot: BunkBot) -> None:
    bot.add_cog(XKCDCog())