import urllib.request
import urllib.parse
import re
import discord
from discord.ext import commands

class Youtube:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def youtube(self, ctx):
        params = ctx.message.content.split()
        if len(params) == 1:
            await self.bot.say("No youtube query given")
            return

        query = urllib.parse.quote_plus(" ".join(params[1:]))
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
        results = list(set(re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())))
        await self.bot.say("https://www.youtube.com/watch?v=" + results[0])

def setup(bot):
    bot.add_cog(Youtube(bot))
