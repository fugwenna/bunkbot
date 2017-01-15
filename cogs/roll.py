from random import randint
from discord.ext import commands
import discord

HELP_DESCRIPTION = """
    Roll a random value
"""

class Roll:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, cls=None, help=HELP_DESCRIPTION)
    async def roll(self, ctx):
        await self.bot.say(embed=discord.Embed(description=str(ctx.message.author).split("#")[0] + " rolls " + str(randint(0, 100))))


def setup(bot):
    bot.add_cog(Roll(bot))
