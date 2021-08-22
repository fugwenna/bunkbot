from typing import List
from discord import Role, Color as DColor
from discord.ext.commands import command, Context, Cog

from .role_service import RoleService
from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_exception import BunkException
from ..core.bunk_user import BunkUser
from ..core.constants import ROLE_SHOW_GAMING
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
    async def print_user_color(user: BunkUser, ctx: Context) -> None:
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
            await ctx.send("{0}, your color role `{1}` has been removed".format(user.mention, role.name))


    # If a color role does not exist and is available,
    # assign it to the requesting user
    async def add_user_color(self, user: BunkUser, color: str, ctx: Context) -> None:
        if color.startswith("#"):
            color = color[1:]

        role_name: str = "color-{0}".format(color)
        self.check_if_role_exists(role_name, user)
        await self.set_user_role(role_name, user, color)
        await ctx.send("{0}, your color role has been set to: `{1}`".format(user.mention, role_name))

    
    # only allow a single color role per user
    def check_if_role_exists(self, role_name: str, user: BunkUser) -> None:
        existing_role: Role = next((r for r in self.bot.server.roles if r.name.lower() == role_name), None)
        
        if existing_role is not None:
            #err_msg: str = "Role `{0}` already exists and is assigned to another user: `{1}`".format(role_name, existing_role.members[0].name)
            is_user: bool = next((r for r in existing_role.members if r.id == user.id), None)

            if is_user is not None:
                err_msg = "`{0}` is already your color role".format(role_name)
                raise BunkException(err_msg)


    # get the color for a role, whether its hex or
    # known color from discord
    def get_color_for_role(self, color: str) -> None:
        discord_color: Color = None

        color_method = [m for m, f in DColor.__dict__.items()]
        for c in color_method:
            if c == color:
                discord_color = getattr(DColor, c)()
                break
                
        try:
            if discord_color is None:
                discord_color = DColor(int(color, 16))
        except Exception:
            raise BunkException("Error assigning color '{0}'".format(color))
        
        if discord_color is None:
            raise BunkException("Error assigning color '{0}'".format(color))

        return discord_color


    # set the color role for a user if
    # it is finally available
    async def set_user_role(self, role_name: str, user: BunkUser, color: str) -> None:
        exists = next((r for r in self.bot.server.roles if r.name.lower() == role_name), None)

        if exists is None:
            pos: int = await self.roles.get_lowest_index_for("color-")
            new_role: Role = await self.roles.add_role_to_user(role_name, user, self.get_color_for_role(color))
            await self.channels.log_info("Elevating role position `{0}` -> `{1}`".format(role_name, pos))
            await new_role.edit(position=pos)
        else:
            await self.channels.log_info("Assigning existing role `{0}` to another user".format(role_name))

        roles: List[Role] = user.member.roles.copy()

        if user.has_role(ROLE_SHOW_GAMING):
            await self.roles.rm_role(ROLE_SHOW_GAMING, user)

        for role in roles:
            if role.name != role_name and "color-"in role.name:
                await self.roles.rm_role(role.name, user)



def setup(bot: BunkBot) -> None:
    bot.add_cog(Color(ROLE_SERVICE, CHANNEL_SERVICE, USER_SERVICE))
