from discord.ext.commands import command
from ..bunkbot import BunkBot
from ..models.bunk_exception import BunkException
from ..services.channel_service import ChannelService
from ..services.role_service import RoleService
from ..services.registry import ROLE_SERVICE, CHANNEL_SERVICE

COLOR_DESCRIPTION = """
Change the color of your name in the chat by using the command !color followed by either a basic
default color, or a hex code.  '!color none' will remove your color.  For assistance with available colors, type !colors \n

Example: !color red
Example: !color #FF0000
"""
class Color:
    def __init__(self, roles: RoleService, channels: ChannelService):
        self.bot: BunkBot = roles.bot
        self.roles: RoleService = roles
        self.channels: ChannelService = channels

    # executable command method which will
    # search and parse out the youtube html
    @command(pass_context=True, help=COLOR_DESCRIPTION, aliases=["c"])
    async def color(self, ctx) -> None:
        try:
            await self.channels.typing(ctx)
        except BunkException as be:
            return # TODO - handle

    # get a list of colors as well as
    # a link to hex color codes
    @command(help="Link to discord API color list and hex code editor")
    async def colors(self) -> None:
        try:
            reg_colors = "Use the classmethod names for a default color (!color red, blue, dark_green, etc) \nhttp://discordpy.readthedocs.io/en/latest/api.html?#discord.Colour.teal"
            hex_colors = "For hex codes, copy the value above the color picker (with the #) and use that value (!color #F70AE8)\nhttps://www.webpagefx.com/web-design/color-picker/"
            await self.bot.say("\n{}\n\n{}".format(reg_colors, hex_colors))
        except Exception as e:
            await self.bot.handle_error(e, "colors")


def setup(bot: BunkBot) -> None:
    bot.add_cog(Color(ROLE_SERVICE, CHANNEL_SERVICE))
