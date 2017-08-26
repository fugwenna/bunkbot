import discord
from discord.ext import commands
from src.bunkbot import BunkBot
from src.util.bunk_user import BunkUser

COLOR_DESCRIPTION = """Change the color of your name in the chat by using the command !color followed by either a basic
    default color, or a hex code.  '!color none' will remove your color.  For assistance with available colors, type !colors \n

    Example: !color red
    Example: !color #FF0000
"""

class Color:
    def __init__(self, bot: BunkBot):
        self.bot = bot


    # get a list of colors as well as
    # a link to hex color codes
    @commands.command(pass_context=False, cls=None, help="Link to discord API color list and hex code editor")
    async def colors(self) -> None:
        try:
            reg_colors = "Use the classmethod names for a default color (!color red, blue, dark_green, etc) \nhttp://discordpy.readthedocs.io/en/latest/api.html?#discord.Colour.teal"
            hex_colors = "For hex codes, copy the value above the color picker (with the #) and use that value (!color #F70AE8)\nhttps://www.webpagefx.com/web-design/color-picker/"
            await self.bot.say("\n{}\n\n{}".format(reg_colors, hex_colors))
        except Exception as e:
            await self.bot.handle_error(e, "colors")


    # executable command method which will
    # search and parse out the youtube html
    @commands.command(pass_context=True, cls=None, help=COLOR_DESCRIPTION, aliases=["c"])
    async def color(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            params = self.bot.get_cmd_params(ctx)
            user: BunkUser = self.bot.get_user(ctx.message.author.name)

            if len(params) == 0:
                if user.color is None: await self.bot.say("You do not have a color role assigned to you")
                else: await self.bot.say("Your current color is '{0}'".format(user.color))
            else:
                color = params[0].lower()

                if color == "none":
                    await self.remove_color_from(user.member)
                    await self.bot.say("Color removed from {0}".format(user.name))
                elif color == user.color:
                    await self.bot.say("You already have the color {0}".format(color))
                else:
                    color_role = "color-{0}".format(color)
                    color_search = [r for r in self.bot.server.roles if color_role == r.name.lower()]

                    if len(color_search) == 0:
                        role = await self.create_color_role(color)
                        await self.replace_color(user, role)
                    else:
                        await self.replace_color(user, color_search[0])

                    await self.bot.say("{0}'s color changed to {1}".format(user.name, color))

                await self.prune_color_roles()
        except Exception as e:
            await self.bot.handle_error(e, "color")
            await self.bot.say("Color '{0}' is not recognized. Type !colors for help".format(color))


    # create a new color role
    async def create_color_role(self, color) -> discord.Role:
        discord_color: None or discord.Color = None

        if color.startswith("#"):
            color = color[1:]

        color_method = [m for m, f in discord.Color.__dict__.items()]
        for c in color_method:
            if c == color:
                discord_color = getattr(discord.Color, c)()
                break

        if discord_color is None:
            discord_color = discord.Color(int(color, 16))

        role = await self.bot.create_role(self.bot.server)
        await self.bot.edit_role(self.bot.server, role, name="color-{0}".format(color), color=discord_color)
        return role


    # only allow a single color for a member
    async def replace_color(self, user: BunkUser, new_color) -> None:
        roles = [new_color]
        for role in user.roles:
            if role.name == new_color or "color-" not in role.name:
                roles.append(role)

        await self.bot.replace_roles(user.member, *roles)


    # remove all colors from a member
    async def remove_color_from(self, member) -> None:
        roles = []
        for role in member.roles:
            if "color-" not in role.name:
                roles.append(role)

        await self.bot.replace_roles(member, *roles)


    # clean up any unused color roles
    async def prune_color_roles(self) -> None:
        for role in self.bot.server.roles:
            if "color-" in role.name:
                role_found = False

                for member in self.bot.server.members:
                    has_role = len([r for r in member.roles if role.name.lower() == r.name.lower()]) > 0
                    if has_role:
                        role_found = True
                        break

                if not role_found:
                    await self.bot.delete_role(self.bot.server, role)


def setup(bot: BunkBot) -> None:
    bot.add_cog(Color(bot))
