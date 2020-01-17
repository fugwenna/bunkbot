from typing import List
from discord import Role
from discord.ext.commands import command, Context, Cog

from .role_service import RoleService
from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_exception import BunkException
from ..core.bunk_user import BunkUser
from ..core.functions import get_cmd_params
from ..core.registry import ROLE_SERVICE, CHANNEL_SERVICE, USER_SERVICE
from ..user.user_service import UserService


COLOR_DESCRIPTION = """
Change the color of your name in the chat by using the command !color followed by either a basic
default color, or a hex code.  '!color none' will remove your color.  For assistance with available colors, type !colors \n

Example: !color red
Example: !color #FF0000
"""
class Color(Cog):
    def __init__(self, roles: RoleService, channels: ChannelService, users: UserService):
        self.bot: BunkBot = roles.bot
        self.roles: RoleService = roles
        self.channels: ChannelService = channels
        self.users: UserService = users


    # executable command method which will
    # search and parse out the youtube html
    @command(help=COLOR_DESCRIPTION, aliases=["c"])
    async def color(self, ctx: Context) -> None:
        try:
            await ctx.send("Not implemented! (i'm in rewrite mode)")
            return

            await ctx.trigger_typing()

            user: BunkUser = self.users.get_by_id(ctx.message.author.id)
            params: List[str] = get_cmd_params(ctx)

            if user is not None:
                if len(params) == 0:
                    await self.print_user_color(user, ctx)
                else:
                    color: str = params[0].lower()

                    if color == "none":
                        await self.remove_user_color(user, ctx)
                    else:
                        await self.add_user_color(user, color, ctx)

            await self.roles.prune_orphaned_roles("color-")
        except BunkException as be:
            await self.channels.log_info(be.message, ctx)
        except Exception as e:
            await self.channels.log_error(e, "colors")


    # get a list of colors as well as
    # a link to hex color codes
    @command(help="Link to discord API color list and hex code editor")
    async def colors(self, ctx: Context) -> None:
        try:
            reg_colors: str = "Use the classmethod names for a default color (!color red, blue, dark_green, etc) \nhttp://discordpy.readthedocs.io/en/latest/api.html?#discord.Colour.teal"
            hex_colors: str = "For hex codes, copy the value above the color picker (with the #) and use that value (!color #F70AE8)\nhttps://www.webpagefx.com/web-design/color-picker/"

            await ctx.send("\n{}\n\n{}".format(reg_colors, hex_colors))
        except Exception as e:
            await self.channels.log_error(e, "colors")


    # when a user doesn't supply any parameters
    # just print their current color, if they have it
    @staticmethod
    async def print_user_color(self, user: BunkUser, ctx: Context) -> None:
        if user.color is None: 
            await ctx.send("You do not have a color role assigned to you")
        else: 
            await ctx.send("Your current color is `{0}`".format(user.color))


    # remove a color from a given user if they supply
    # the command flag of 'none'
    async def remove_user_color(self, user: BunkUser, ctx: Context) -> None:
        role: Role = await self.roles.get_role_containing("color-", user)

        if role is not None:
            await self.roles.rm_role(role.name, user)
            await ctx.send("Your color role `{0}` has been removed".format(role.name))


    # If a color role does not exist and is available,
    # assign it to the requesting user
    async def add_user_color(self, user: BunkUser, color: str, ctx: Context) -> None:
        role_name: str = "color-{0}".format(color)
        self.check_if_role_exists(role_name, user)
        await self.set_user_role(role_name, user)

    
    # only allow a single color role per user
    def check_if_role_exists(self, role_name: str, user: BunkUser) -> None:
        existing_role: Role = next((r for r in self.bot.server.roles if r.name.lower() == role_name), None)
        
        if existing_role is not None:
            err_msg: str = "Role `{0}` already exists and is assigned to another user".format(role_name)
            is_user: bool = next((r for r in existing_role.members if r.id == user.id), None)

            if is_user is not None:
                err_msg = "`{0}` is already your color role".format(role_name)

            raise BunkException(err_msg)


    # set the color role for a user if
    # it is finally available
    async def set_user_role(self, role_name: str, user: BunkUser) -> None:
        pass


def setup(bot: BunkBot) -> None:
    bot.add_cog(Color(ROLE_SERVICE, CHANNEL_SERVICE, USER_SERVICE))
