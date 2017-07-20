"""
Discord.py wrapper class which inherits the
Bot class as it's parent
"""
from os import walk
from os.path import join, splitext, sep

import json, urllib.request, discord
from discord.ext import commands

from src.storage.db import database


BOT_DESCRIPTION = """
The bunkest bot - type '!help' for myt commands, or say my name to chat with me.\n
My source code: https://github.com/fugwenna/bunkbot
"""

class BunkBot(commands.Bot):
    def __init__(self):
        super().__init__("!", None, BOT_DESCRIPTION, False)
        self.init: bool = False
        self.server: discord.Server = None
        self.bot_testing: discord.Channel = None
        self.mod_chat: discord.Channel = None
        self.vip_chat: discord.Channel = None


    # lifecycle hook - set up all
    # of the necessary and useful channels
    async def on_init(self):
        if self.init is False:
            self.init = True
            self.server: discord.Server = self.get_server(database.get("serverid"))
            self.bot_testing = [ch for ch in self.server.channels if ch.name == "bot-testing"][0]
            self.mod_chat = [ch for ch in self.server.channels if ch.name == "mod-chat"][0]
            self.vip_chat = [ch for ch in self.server.channels if ch.name == "vip-chat"][0]
            self.load_cogs()
            self.sync_users()


    # update the cogs database when
    # new cogs are added to the db
    def load_cogs(self) -> None:
        for path, dirs, files in walk(join("src", "cogs")):
            for f in files:
                file_path = join(path, f)
                cog_split = file_path.split("_")
                if len(cog_split) > 1 and cog_split[1] == "cog.py":
                    sep_split = file_path.split(sep)
                    sep_split[len(sep_split)-1] = splitext(sep_split[len(sep_split)-1])[0]
                    self.load_extension(".".join(sep_split))


    # sync the current server users with
    # those that already exist in the database
    def sync_users(self) -> None:
        for m in self.server.members:
            member: discord.Member = m
            #member.name


    # greet a new member with a simple message,
    # apply the "new" role, and update the database
    async def member_join(self, member: discord.Member) -> None:
        server = member.server
        fmt = "Welcome {0.mention} to {1.name}!  Type !help for a list of my commands"
        await self.send_message(server, fmt.format(member, server))


    # perform custom functions when a user has
    # been updated - i.e. apply custom/temporary roles
    async def member_update(self, before: discord.Member, after: discord.Member) -> None:
        pass


    # process each message that is sent
    # to the server - if bunkbot is chatting, continue to chat
    # otherwise, process the message as a command
    async def process_message(self, message: discord.Message) -> None:
        # todo - rewire chat bot stuff
        await self.process_commands(message)


    # retrieve an array of the passed
    # message command arguments
    @staticmethod
    def get_cmd_params(ctx: commands.Context) -> list:
        if ctx is not None:
            return ctx.message.content.split()[1:]
        else:
            return ""


    # retrieve the author of the
    # given context
    @staticmethod
    def get_author(ctx, with_id=False) -> str:
        author = str(ctx.message.author)

        if not with_id:
            author = author.split("#")[0]

        return author


    # send an embedded message to the server
    # using known **kwargs in the ctor
    async def say_embed(self, **kwargs) -> None:
        embed: discord.Embed = discord.Embed(**kwargs)

        #if footer is not None and footer_icon is not None:
        #    embed.set_footer(text=footer, icon_url=footer_icon)
        #elif footer is not None:
        #    embed.set_footer(text=footer)

        #if image is not None:
        #    embed.set_thumbnail(url=image)

        return await self.say(embed=embed)


    # send a message to a specific channel
    async def say_to_channel(self, channel: discord.Channel, message: str) -> None:
        try:
            self.send_typing(channel)
            await self.send_message(channel, message)
        except Exception as e:
            await self.handle_error(e, "say_to_channel")


    # make a basic http call
    # with urllib
    @staticmethod
    def http_get(url) -> json:
        return json.loads(urllib.request.urlopen(url).read())


    # default catch for handling any errors that
    # occur when processing bot commands
    async def handle_error(self, error: str, command: str, say_error=True) -> None:
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