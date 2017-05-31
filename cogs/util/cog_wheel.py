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
    async def send_message(self, title, msg, image=None, footer=None, footer_icon=None, color=discord.Embed.Empty):
        embed = discord.Embed(title=title, description=msg, color=color)

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
    async def handle_error(self, error, command, say_error=True):
        try:
            if say_error:
                await self.send_message_plain("Ahh Error!")

            if self.server is None:
                with open("config.json", "r") as config:
                    conf = json.load(config)
                    self.server = self.bot.get_server(conf["serverid"])

            if self.bot_testing is None:
                self.bot_testing = [ch for ch in self.server.channels if ch.name == "bot-testing"][0]

            if str(error) == "":
                error = "Unknown"

            await self.bot.send_message(self.bot_testing, "Error occured from command '" + command + "': " + str(error))
        except Exception as e:
            print(e)

    """
    Send a message to a given channel
    """
    async def send_message_to_channel(self, channel, message):
        try:
            await self.bot.send_message(channel, message)
        except Exception as e:
            await self.handle_error(e, "send_message_to_channel")

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
    
