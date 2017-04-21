from discord.ext import commands
from .util.cog_wheel import CogWheel
import json

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
                if len(color_roles) == 0:
                    await self.send_message_plain("You do not have a color role assigned to you")
                else:
                    await self.send_message_plain("Your current color is {}".format(color_roles[0].split("_")[1]))
            else:
                #color = params[1]
                await self.coming_soon()
                return
            
        except Exception as e:
            print(e)
            await self.send_message_plain("Color unrecognized")

            
def setup(bot):
    with open("config.json", "r") as config:
        conf = json.load(config)
        bot.add_cog(Color(bot, conf["serverid"]))
