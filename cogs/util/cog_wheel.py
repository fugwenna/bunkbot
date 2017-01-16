import discord

"""
Primary base class that will just
wrap commonly used bot extension
methods (i.e. bot.say, discord.Embed, etc)
"""
class CogWheel:
    def __init__(self, bot):
        self.bot = bot

    """
    Send a message as a basic
    discord Embed class message - this
    will be the default message type
    """
    async def send_message(self, title, msg):
        await self.bot.say(embed=discord.Embed(title=title, description=msg))

    """
    Send a plain non discord Embed message
    """
    async def send_message_plain(self, msg):
        await self.bot.say(msg)

    """
    Even more wrapping around editing
    a previous sent message from the bot
    """
    async def edit_message(self, msg, new_content=None):
        await self.bot.edit_message(msg, new_content)

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
        return ctx.message.content.split()[1:]
