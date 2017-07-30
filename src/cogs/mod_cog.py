"""
Commands only allowable by admin, moderator, and vip users
"""
from discord.ext import commands
from ..bunkbot import BunkBot

class Mod:
    def __init__(self, bot: BunkBot):
        self.bot = bot


    # get info on a particular user
    # preferably their role(s) - otherwise
    # check names, nicks secondary - in channel?
    @commands.has_any_role("admin", "moderator")
    @commands.command(pass_context=True, cls=None, help="Retrieve user information")
    async def who(self, ctx):
        # i.e.   !who streaming
        # returns anyone who has 'streaming' role
        pass


def setup(bot: BunkBot):
    bot.add_cog(Mod(bot))