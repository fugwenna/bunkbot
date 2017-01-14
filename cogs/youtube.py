import urllib.request
import urllib.parse
import re
import discord
from bs4 import BeautifulSoup
from discord.ext import commands

HELP_DESCRIPTION = """
    Search for a youtube video (alias: yt)

    example: !youtube heroes of the storm
"""

class Youtube:
    def __init__(self, bot):
        self.bot = bot
        self.ids = []
        self.message = None

    """
    Executable command method which will
    search and parse out the youtube html
    """
    async def cmd(self, ctx):
        self.ids = []
        params = ctx.message.content.split()
        titles = []

        if len(params) == 1:
            await self.bot.say("No youtube query given")
            return

        html = self.parse_query(" ".join(params[1:]))
        items = BeautifulSoup(html, "html.parser").find("ol", class_="item-section")
        ahref = BeautifulSoup(str(items), "html.parser").find_all("a")

        i = 0
        for result in ahref:
            if i == 5:
                break


            href = result["href"]
            title = result.get("title")
            if re.match(r'\/watch\?v=(.{11})', href) and title is not None:
                i+=1
                self.ids.append(href.split("=")[1])

                #if i > 0:
                #    parent = result.find_parent()
                #    sibs = parent.next_siblings("div")
                #    for sib in sibs:
                #        if sib.get("class") == "yt-lockup-byline":
                #            anc = sib.find("a")
                #            print(anc)

                titles.append("{0}. {1}".format(i, title))


        if (len(self.ids) == 0):
            await self.bot.say("No ids found for " + query)
            return

        await self.link_video(self.ids[0])
        await self.bot.say(embed=discord.Embed(title="\nNot the video you're looking for? type \"!ytl\" 1-5 to link another video\n", description="\n".join(titles)))


    """
    Parse the given query string into a encoded url
    and open the url to read the html contents
    """
    def parse_query(self, query):
        query = urllib.parse.quote_plus(query)
        response = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
        html = response.read().decode()
        response.close()
        return html
    
    """
    Link the video in the chat
    """
    async def link_video(self, video):
        self.message = await self.bot.say("https://www.youtube.com/watch?v=" + video)

    @commands.command(pass_context=True, cls=None, help=HELP_DESCRIPTION)
    async def youtube(self, ctx):
        await self.cmd(ctx)

    @commands.command(pass_context=True, cls=None, help=HELP_DESCRIPTION)
    async def yt(self, ctx):
        await self.cmd(ctx)

    @commands.command(pass_context=True)
    async def ytl(self, ctx):
        params = ctx.message.content.split()
        if len(params) == 1 or not params[1].isdigit() or int(params[1]) > len(self.ids) or int(params[1]) < 0:
            await self.bot.say("Please enter a valid video number from 1 to 5")
            return

        self.message = await self.bot.edit_message(self.message, "https://www.youtube.com/watch?v=" + self.ids[(int(params[1])-1)])


def setup(bot):
    bot.add_cog(Youtube(bot))
