"""
Commands only allowable by admin, moderator, and vip
"""
from discord.ext import commands
from discord.ext.commands import command
from src.bunkbot import BunkBot


class Vip:
    def __init__(self, bot: BunkBot):
        self.bot = bot


def setup(bot: BunkBot):
    bot.add_cog(Vip(bot))