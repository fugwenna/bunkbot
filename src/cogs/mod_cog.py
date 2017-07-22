"""
Commands only allowable by admin, moderator, and vip users
"""
from discord.ext import commands
from ..bunkbot import BunkBot

class Mod:
    def __init__(self, bot: BunkBot):
        self.bot = bot


def setup(bot: BunkBot):
    bot.add_cog(Mod(bot))