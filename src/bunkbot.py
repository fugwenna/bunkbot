"""
Discord.py wrapper class which inherits the
Bot class as it's parent
"""
import json, urllib.request, discord
from os import walk
from os.path import join, splitext, sep
from discord.ext import commands
from src.storage.db import database

BOT_DESCRIPTION = """
The bunkest bot - type '!help' for myt commands, or say my name to chat with me. Type '!help [command] for more info
on a command (i.e. !help color)\n

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
        self.load_cogs()


    # lifecycle hook - set up all
    # of the necessary and useful channels
    async def on_init(self):
        if self.init is False:
            self.init = True
            self.server: discord.Server = self.get_server(database.get("serverid"))
            self.bot_testing = [ch for ch in self.server.channels if ch.name == "bot-testing"][0]
            self.mod_chat = [ch for ch in self.server.channels if ch.name == "mod-chat"][0]
            self.vip_chat = [ch for ch in self.server.channels if ch.name == "vip-chat"][0]
            await self.say_to_channel(self.bot_testing, "Bot and database initialized. Syncing users...")
            await self.sync_users()


    # update the cogs database when
    # new cogs are added to the db
    def load_cogs(self) -> None:
        try:
            for path, dirs, files in walk(join("src", "cogs")):
                for f in files:
                    file_path = join(path, f)
                    cog_split = file_path.split("_")
                    if len(cog_split) > 1 and cog_split[1] == "cog.py":
                        sep_split = file_path.split(sep)
                        sep_split[len(sep_split)-1] = splitext(sep_split[len(sep_split)-1])[0]
                        self.load_extension(".".join(sep_split))
        except Exception as e:
            print(e)


    # sync the current server users with
    # those that already exist in the database
    async def sync_users(self) -> None:
        try:
            new_users = []
            for member in self.server.members:
                user_added: bool = database.check_user(member)
                if user_added:
                    new_users.append(member.name)

            if len(new_users) > 0:
                new_user_list: str = "\n".join(new_users)
                new_user_msg: str = "Users synced. The following users have been added to the database: \n{0}".format(new_user_list)
                await self.say_to_channel(self.bot_testing, new_user_msg)
                await self.say_to_channel(self.mod_chat, new_user_msg)
            else:
                await self.say_to_channel(self.bot_testing, "Users synced. No new users added to database.")
        except Exception as e:
            self.handle_error(e, "sync_users", False)


    # send an embedded message to the server
    # using known **kwargs in the ctor
    async def say_embed(self, embed: discord.Embed) -> None:
        try:
            return await self.say(embed=embed)
        except Exception as e:
            self.handle_error(e, "say_embed")


    # send a message to a specific channel instead
    # of the normal channel of the message context object
    async def say_to_channel(self, channel: discord.Channel, message: str) -> None:
        try:
            self.send_typing(channel)
            await self.send_message(channel, message)
        except Exception as e:
            await self.handle_error(e, "say_to_channel")


    # process each message that is sent
    # to the server - if bunkbot is chatting, continue to chat
    # otherwise, process the message as a command
    async def process_message(self, message: discord.Message) -> None:
        try:
            # todo - rewire chat bot stuff
            await self.process_commands(message)
        except Exception as e:
            self.handle_error(e, "process_message")


    # greet a new member with a simple message,
    # apply the "new" role, and update the database
    async def member_join(self, member: discord.Member) -> None:
        try:
            server = member.server
            fmt = "Welcome {0.mention} to {1.name}!  Type !help for a list of my commands"

            database.check_user(member)
            await self.say_to_channel(self.bot_testing, "New member '{0}' has been added to the database".format(member.name))
            await self.say_to_channel(self.mod_chat, "New member '{0}' has been added to the database".format(member.name))

            await self.send_message(server, fmt.format(member, server))
        except Exception as e:
            self.handle_error(e, "member_join")


    # perform custom functions when a user has
    # been updated - i.e. apply
    #  custom/temporary roles
    async def member_update(self, before: discord.Member, after: discord.Member) -> None:
        try:
            # todo - move this to another method?
            stream_role = [r for r in after.server.roles if r.name == "streaming"][0]
            member_streaming = [r for r in after.roles if r.name == "streaming"]

            if after.game is not None and after.game.type == 1:
                if len(member_streaming) == 0:
                    await self.bot.add_roles(after, stream_role)

            elif before.game is not None and before.game.type == 1:
                if len(member_streaming) > 0:
                    await self.bot.remove_roles(after, stream_role)
        except Exception as e:
            self.handle_error(e, "member_update")


    # alert when a member has been "removed" from the server
    # no way to distinguish a kick or leave, only ban events
    async def member_remove(self, member: discord.Member):
        try:
           await self.say_to_channel(self.mod_chat, "User '{0}' has left the server.".format(member.name))
        except Exception as e:
            self.handle_error(e, "member_update")


    # make a basic http call
    # with urllib
    def http_get(self, url) -> json:
        try:
            return json.loads(urllib.request.urlopen(url).read())
        except Exception as e:
            self.handle_error(e, "http_get")


    # retrieve an array of the passed
    # message command arguments
    @staticmethod
    def get_cmd_params(ctx: commands.Context) -> list:
        if ctx is not None:
            return ctx.message.content.split()[1:]
        else:
            return []


    # retrieve the author of the
    # given context
    @staticmethod
    def get_author(ctx, with_id=False) -> str:
        author = str(ctx.message.author)

        if not with_id:
            author = author.split("#")[0]

        return author


    # default catch for handling any errors that
    # occur when processing bot commands
    async def handle_error(self, error: str, command: str, say_error: bool = True) -> None:
        try:
            if say_error:
                await self.say("Ahh Error!")

            error_message = "Error occurred from command '{0}': {1}".format(command, error)

            await self.say_to_channel(self.bot_testing, error_message)
        except Exception as e:
            print(e)


bunkbot = BunkBot()