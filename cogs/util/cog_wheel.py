import json, urllib.request
import discord

"""
Primary base class that will just
wrap commonly used bot extension
methods (i.e. bot.say, discord.Embed, etc)
"""
class CogWheel:
    def __init__(self, bot):
        self.bot = bot
        self.server = None
        self.bot_testing = None

    """
    Send a message as a basic
    discord Embed class message - this
    will be the default message type
    """
    async def send_message(self, title, msg, image=None, footer=None, footer_icon=None):
        embed = discord.Embed(title=title, description=msg)

        if footer is not None and footer_icon is not None:
            embed.set_footer(text=footer, icon_url=footer_icon)
        elif footer is not None:
            embed.set_footer(text=footer)

        if image is not None:
            embed.set_thumbnail(url=image)
            
        return await self.bot.say(embed=embed)

    """
    Send a plain non discord Embed message
    """
    async def send_message_plain(self, msg):
        return await self.bot.say(msg)

    """
    Even more wrapping around editing
    a previous sent message from the bot
    """
    async def edit_message(self, msg, new_content=None):
        return await self.bot.edit_message(msg, new_content)

    """
    Retrieve the author of a command
    from the context object
    """
    def get_author(self, ctx, with_id=False):
        author = str(ctx.message.author)

        if not with_id:
            author = author.split("#")[0]

        return author

    """
    Retrieve an array of the passed
    message command arguments
    """
    def get_cmd_params(self, ctx):
        if ctx is not None:
            return ctx.message.content.split()[1:]
        else:
            return ""


    """
    Handle an error
    """
    async def handle_error(self, error):
        await self.send_message_plain("Ahh Error!")
        #await self.bot.send_message("bot-testing", str(error))

    """
    Display a coming soon message
    """
    async def coming_soon(self):
        return await self.send_message_plain("Coming Soon™")

    """
    Make an http get call
    """
    def http_get(self, url):
        return json.loads(urllib.request.urlopen(url).read())
    
