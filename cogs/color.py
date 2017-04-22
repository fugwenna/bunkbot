from discord.ext import commands
from .util.cog_wheel import CogWheel
import json, discord

HELP_DESCRIPTION = """
    COMING SOON!!! Change your color!!!! hex or named
"""
class Color(CogWheel):
    def __init__(self, bot, token):
        CogWheel.__init__(self, bot)
        self.token = token
        self.server = None
            
    """
    Executable command method which will
    search and parse out the youtube html
    """
    @commands.command(pass_context=True, cls=None, help=HELP_DESCRIPTION)
    async def color(self, ctx):
        try:
            await self.bot.send_typing(ctx.message.channel)

            if self.server is None:
                self.server = self.bot.get_server(self.token)
            
            params = self.get_cmd_params(ctx)
            member = self.server.get_member_named(str(ctx.message.author))
            
            color_roles = [];
            for role in member.roles:
                if "color_" in role.name:
                    color_roles.append(role.name)

            if len(params) == 0:
                self.print_member_color(member, color_roles)
            else:
                if params[0].lower() == "none":
                    await self.remove_colors(member)
                    await self.send_message_plain("Color removed from {}".format(member.name))
                else:
                    color = params[0]
                    color_role = "color_{}".format(params[0])

                    if len([r for r in member.roles if color_role in r.name]) > 0:
                        await self.send_message_plain("You already have the color {}".format(color))
                        return
                    
                    exists = [r for r in self.server.roles if color_role in r.name]

                    if len(exists) == 0:
                        role = await self.create_color_role(color)
                        await self.replace_color(member, role)
                    else:
                        await self.replace_color(member, exists[0])

                    await self.send_message_plain("{}'s color changed to {}".format(member.name, color))
                    
                await self.prune_color_roles()
        except Exception as e:
            print("ERROR: " + str(e))
            await self.send_message_plain("Color '{}' is not recognized".format(color))

    """
    Print a users existing color
    """
    async def print_member_color(self, member, color_roles):
        if len(color_roles) == 0:
            await self.send_message_plain("You do not have a color role assigned to you. Ex: Type !color red to change your color to red")
        else:
            await self.send_message_plain("Your current color is {}".format(color_roles[0].split("_")[1]))

    """
    Create a new color role
    """
    async def create_color_role(self, color):
        color_method = [m for m,f in discord.Color.__dict__.items()]
        
        if color.startswith("#"):
            dcolor = discord.Color(int(color[1:], 16))
            role = await self.bot.create_role(self.server)
            await self.bot.edit_role(self.server, role, name="color_{}".format(color), color=dcolor)
            return role
        else:
            for c in color_method:
                if c == color:
                    dcolor = getattr(discord.Color, c)()
                    role = await self.bot.create_role(self.server)
                    await self.bot.edit_role(self.server, role, name="color_{}".format(color), color=dcolor)
                    return role
            
            dcolor = discord.Color(int(color, 16))
            role = await self.bot.create_role(self.server)
            await self.bot.edit_role(self.server, role, name="color_#{}".format(color), color=dcolor)
            return role

    """
    Only allow a single color for a member
    """
    async def replace_color(self, member, new_color):
        roles = [new_color]
        for role in member.roles:
            if role.name == new_color or "color_" not in role.name:
                roles.append(role)

        await self.bot.replace_roles(member, *roles)

    """
    Remove all colors from a member
    """
    async def remove_colors(self, member):
        roles = []
        for role in member.roles:
            if "color_" not in role.name:
                roles.append(role)

        await self.bot.replace_roles(member, *roles)
        

    """
    Clean up any unused color roles
    """
    async def prune_color_roles(self):
        for role in self.server.roles:
            if "color_" in role.name:
                role_found = False
                
                for member in self.server.members:
                    has_role = len([r for r in member.roles if role.name == r.name]) > 0
                    if has_role:
                        role_found = True
                        break

                if not role_found:
                    await self.bot.delete_role(self.server, role)

def setup(bot):
    with open("config.json", "r") as config:
        conf = json.load(config)
        bot.add_cog(Color(bot, conf["serverid"]))
