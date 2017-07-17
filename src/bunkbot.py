"""
Discord.py wrapper class which inherits the
Bot class as it's parent
"""
import discord
from discord.ext import commands
from .storage.db import database

BOT_DESCRIPTION = """
The bunkest bot - type '!help' for myt commands, or say my name to chat with me.\n
My source code: https://github.com/fugwenna/bunkbot
"""

class BunkBot(commands.Bot):
    # establish the command prefix
    # and bot description for the commands.Bot
    def __init__(self):
        super().__init__(self)
        self.command_prefix = "!"
        self.description = BOT_DESCRIPTION

    # greet a new member with a simple message,
    # apply the "new" role, and update the database
    async def on_member_join(self, member: discord.Member):
        server = member.server
        fmt = "Welcome {0.mention} to {1.name}!  Type !help for a list of my commands"
        await self.send_message(server, fmt.format(member, server))


    # perform custom functions when a user has
    # been updated - i.e. apply custom/temporary roles
    async def on_member_update(self, member: discord.Member):
        await self.send_message(member.server, "todo!")


    # process each message that is sent
    # to the server - if bunkbot is chatting, continue to chat
    # otherwise, process the message as a command
    async def process_message(self, message: discord.Message):
        await self.process_commands(message)


    # default catch for handling any errors that
    # occur when processing bot commands
    async def handle_error(self, error: str, command: str, say_error=True):
        try:
            await self.send_message("Error!")
            # if say_error:
            #     await self.send_message_plain("Ahh Error!")
            #
            # if self.server is None:
            #     with open("config.json", "r") as config:
            #         conf = json.load(config)
            #         self.server = self.bot.get_server(conf["serverid"])
            #
            # if self.bot_testing is None:
            #     self.bot_testing = [ch for ch in self.server.channels if ch.name == "bot-testing"][0]
            #
            # if str(error) == "":
            #     error = "Unknown"
            #
            # await self.bot.send_message(self.bot_testing,
            #                             "Error occured from command '" + command + "': " + str(error))
        except Exception as e:
            print(e)


bunkbot = BunkBot()