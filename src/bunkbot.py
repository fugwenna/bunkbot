"""
Discord.py wrapper class which inherits the
Bot class as it's parent
"""
from os import walk
from os.path import join, splitext, sep

import discord
from discord.ext import commands

BOT_DESCRIPTION = """
The bunkest bot - type '!help' for myt commands, or say my name to chat with me.\n
My source code: https://github.com/fugwenna/bunkbot
"""

class BunkBot(commands.Bot):
    def __init__(self):
        super().__init__("!", None, BOT_DESCRIPTION, False)
        self.load_cogs()


    # update the cogs database when
    # new cogs are added to the db
    def load_cogs(self):
        for path, dirs, files in walk(join("src", "cogs")):
            for f in files:
                file_path = join(path, f)
                cog_split = file_path.split("_")
                if len(cog_split) > 1 and cog_split[1] == "cog.py":
                    sep_split = file_path.split(sep)
                    sep_split[len(sep_split)-1] = splitext(sep_split[len(sep_split)-1])[0]
                    self.load_extension(".".join(sep_split))


    # greet a new member with a simple message,
    # apply the "new" role, and update the database
    async def member_join(self, member: discord.Member):
        server = member.server
        fmt = "Welcome {0.mention} to {1.name}!  Type !help for a list of my commands"
        await self.send_message(server, fmt.format(member, server))


    # perform custom functions when a user has
    # been updated - i.e. apply custom/temporary roles
    async def member_update(self, before: discord.Member, after: discord.Member):
        await self.say("todo!")


    # process each message that is sent
    # to the server - if bunkbot is chatting, continue to chat
    # otherwise, process the message as a command
    async def process_message(self, message: discord.Message):
        # todo - rewire chat bot stuff
        await self.process_commands(message)


    # retrieve an array of the passed
    # message command arguments
    @staticmethod
    def get_cmd_params(ctx: commands.Context):
        if ctx is not None:
            return ctx.message.content.split()[1:]
        else:
            return ""


    # retrieve the author of the
    # given context
    @staticmethod
    def get_author(ctx, with_id=False):
        author = str(ctx.message.author)

        if not with_id:
            author = author.split("#")[0]

        return author


    # send an embedded message to the server
    # using known **kwargs in the ctor
    async def send_embed_message(self, **kwargs):
        embed: discord.Embed = discord.Embed(**kwargs)

        #if footer is not None and footer_icon is not None:
        #    embed.set_footer(text=footer, icon_url=footer_icon)
        #elif footer is not None:
        #    embed.set_footer(text=footer)

        #if image is not None:
        #    embed.set_thumbnail(url=image)

        return await self.say(embed=embed)


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