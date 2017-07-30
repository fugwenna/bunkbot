import discord
from discord.ext import commands
from ..bunkbot import BunkBot

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
    async def colors(self):
        try:
            reg_colors = "Use the classmethod names for a default color (!color red, blue, dark_green, etc) \nhttp://discordpy.readthedocs.io/en/latest/api.html?#discord.Colour.teal"
            hex_colors = "For hex codes, copy the value above the color picker (with the #) and use that value (!color #F70AE8)\nhttps://www.webpagefx.com/web-design/color-picker/"
            await self.bot.say("\n{}\n\n{}".format(reg_colors, hex_colors))
        except Exception as e:
            await self.bot.handle_error(e, "colors")


    # executable command method which will
    # search and parse out the youtube html
    @commands.command(pass_context=True, cls=None, help=COLOR_DESCRIPTION)
    async def color(self, ctx):
        try:
            await self.bot.send_typing(ctx.message.channel)

            params = self.bot.get_cmd_params(ctx)
            member = self.bot.server.get_member_named(str(ctx.message.author))

            color_roles = []
            for role in member.roles:
                if "color_" in role.name:
                    color_roles.append(role.name)

            if len(params) == 0:
                await self.print_member_color(member, color_roles)
            else:
                if params[0].lower() == "none":
                    await self.remove_colors(member)
                    await self.bot.say("Color removed from {}".format(member.name))
                else:
                    color = params[0]
                    color_role = "color_{}".format(params[0])

                    if len([r for r in member.roles if color_role in r.name]) > 0:
                        await self.bot.say("You already have the color {}".format(color))
                        return

                    exists = [r for r in self.bot.server.roles if color_role in r.name]

                    if len(exists) == 0:
                        role = await self.create_color_role(color)
                        await self.replace_color(member, role)
                    else:
                        await self.replace_color(member, exists[0])

                    # await self.send_message("Color change", "{}'s color changed to {}".format(member.name, color), None, None, None, role.color)
                    await self.bot.say("{}'s color changed to {}".format(member.name, color))

                await self.prune_color_roles()
        except Exception as e:
            await self.bot.handle_error(e, "color", False)
            await self.bot.say("Color '{}' is not recognized. Type !colors for help".format(color))


    # print a users existing color
    async def print_member_color(self, member, color_roles):
        if len(color_roles) == 0:
            await self.bot.say(
                "You do not have a color role assigned to you. Ex: Type !color red to change your color to red")
        else:
            await self.bot.say("Your current color is {}".format(color_roles[0].split("_")[1]))


    # create a new color role
    async def create_color_role(self, color):
        if color.startswith("#"):
            dcolor = discord.Color(int(color[1:], 16))
            role = await self.bot.create_role(self.bot.server)
            await self.bot.edit_role(self.bot.server, role, name="color_{}".format(color), color=dcolor)
            return role
        else:
            color_method = [m for m, f in discord.Color.__dict__.items()]
            for c in color_method:
                if c == color:
                    dcolor = getattr(discord.Color, c)()
                    role = await self.bot.create_role(self.bot.server)
                    await self.bot.edit_role(self.bot.server, role, name="color_{}".format(color), color=dcolor)
                    return role

            dcolor = discord.Color(int(color, 16))
            role = await self.bot.create_role(self.bot.server)
            await self.bot.edit_role(self.bot.server, role, name="color_#{}".format(color), color=dcolor)
            return role


    # only allow a single color for a member
    async def replace_color(self, member, new_color):
        roles = [new_color]
        for role in member.roles:
            if role.name == new_color or "color_" not in role.name:
                roles.append(role)

        await self.bot.replace_roles(member, *roles)


    # remove all colors from a member
    async def remove_colors(self, member):
        roles = []
        for role in member.roles:
            if "color_" not in role.name:
                roles.append(role)

        await self.bot.replace_roles(member, *roles)


    # clean up any unused color roles
    async def prune_color_roles(self):
        for role in self.bot.server.roles:
            if "color_" in role.name:
                role_found = False

                for member in self.bot.server.members:
                    has_role = len([r for r in member.roles if role.name == r.name]) > 0
                    if has_role:
                        role_found = True
                        break

                if not role_found:
                    await self.bot.delete_role(self.bot.server, role)


def setup(bot: BunkBot) -> None:
    bot.add_cog(Color(bot))
