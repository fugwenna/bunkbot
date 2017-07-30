"""
Discord.py wrapper class which inherits the
Bot class as it's parent
"""
import json, urllib.request, discord, re, time, sys, traceback
from cleverwrap import CleverWrap
from os import walk
from os.path import join, splitext, sep
from discord.ext import commands
from src.storage.db import database

BOT_DESCRIPTION = """
The bunkest bot - type '!help' for my commands, or say my name to chat with me. Type '!help [command] for more info
on a command (i.e. !help color)\n
"""

class BunkBot(commands.Bot):
    def __init__(self):
        super().__init__("!", None, BOT_DESCRIPTION, False)
        self.init: bool = False
        self.chat_timer = 9.5
        self.last_message_at = -1
        self.chat_bot: CleverWrap = None
        self.server: discord.Server = None
        self.bot_testing: discord.Channel = None
        self.mod_chat: discord.Channel = None
        self.vip_chat: discord.Channel = None
        self.role_streaming = None
        self.load_cogs()


    # lifecycle hook - set up all
    # of the necessary and useful channels
    async def on_init(self):
        if self.init is False:
            self.init = True
            self.server = self.get_server(database.get("serverid"))
            self.role_streaming = [r for r in self.server.roles if r.name == "streaming"][0]

            for ch in self.server.channels:
                if ch.name == "bot-testing":
                    self.bot_testing = ch
                elif ch.name == "mod-chat":
                    self.mod_chat = ch
                elif ch.name == "vip-chat":
                    self.vip_chat = ch

            self.chat_bot = CleverWrap(database.get("cleverbot"))
            await self.say_to_channel(self.bot_testing, "Bot and database initialized. Syncing users and channels...")
            await self.sync_users()
            await self.sync_channels()


    # update the cogs database when
    # new cogs are added to the db
    @staticmethod
    def get_author(ctx: commands.Context, with_id=False) -> str:
        author: str = str(ctx.message.author)

        if not with_id:
            author = author.split("#")[0]

        return author


    # retrieve an array of the passed
    # message command arguments
    @staticmethod
    def get_cmd_params(ctx: commands.Context) -> list:
        if ctx is not None:
            return ctx.message.content.split()[1:]
        else:
            return []


    # check if the bot is still
    # having a conversation with someone
    @property
    def is_chatting(self):
        new_time = time.time() - self.last_message_at
        still_chatting = new_time < self.chat_timer

        if not still_chatting:
            self.last_message_at = -1

        return still_chatting


    # retrieve the author of the
    # given context
    def load_cogs(self) -> None:
        try:
            for path, dirs, files in walk(join("src", "cogs")):
                for f in files:
                    file_path: str = join(path, f)
                    cog_split: list = file_path.split("_")
                    if len(cog_split) > 1 and cog_split[1] == "cog.py":
                        sep_split: list = file_path.split(sep)
                        sep_split[len(sep_split)-1] = splitext(sep_split[len(sep_split)-1])[0]
                        self.load_extension(".".join(sep_split))
        except Exception as e:
            print(e)


    # sync the current server users with
    # those that already exist in the database
    async def sync_users(self) -> None:
        try:
            new_users: list = []
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


    # update the channel references
    # to
    async def sync_channels(self) -> None:
        try:
            pass
        except Exception as e:
            self.handle_error(e, "sync_channels", False)


    # process each message that is sent
    # to the server - if bunkbot is chatting, continue to chat
    # otherwise, process the message as a command
    async def process_message(self, message: discord.Message) -> None:
        try:
            if message.author.bot:
                return

            is_reset = message.content == "!reset"
            is_bunk_mention = len(message.mentions) > 0 and message.mentions[0].name == "BunkBot"
            content = re.findall("[a-zA-Z]+", str(message.content).upper())

            if not is_reset and (self.is_chatting or (is_bunk_mention or "BUNKBOT" in content)):
                await self.chat(message)
            else:
                await self.process_commands(message)

            if is_reset:
                await self.delete_message(message)
        except Exception as e:
            await self.handle_error(e, "process_message")


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
            # todo test if await is needed
            await self.send_message(channel, message)
        except Exception as e:
            await self.handle_error(e, "say_to_channel")


    # have a cleverbot conversation with
    # a user if they say the name 'bunkbot'
    async def chat(self, message: discord.Message) -> None:
        await self.send_typing(message.channel)
        content = re.sub(r'bunkbot', "", str(message.content), flags=re.IGNORECASE).strip()

        # if the user just says 'bunkbot'
        # treat it as a greeting
        if content == "":
            content = "Hello!"

        await self.send_message(message.channel, self.chat_bot.say(content))
        self.last_message_at = time.time()


    # greet a new member with a simple message,
    # apply the "new" role, and update the database
    async def member_join(self, member: discord.Member) -> None:
        try:
            server: discord.Server = member.server
            fmt: str = "Welcome {0.mention} to {1.name}!  Type !help for a list of my commands"

            database.check_user(member)
            await self.say_to_channel(self.mod_chat, "New user '{0}' has joined the server and added to the database".format(member.name))

            await self.send_message(server, fmt.format(member, server))
        except Exception as e:
            self.handle_error(e, "member_join")


    # perform custom functions when a user has
    # been updated - i.e. apply custom/temporary roles
    async def member_update(self, before: discord.Member, after: discord.Member) -> None:
        try:
            await self.check_user_streaming(before, after)
        except Exception as e:
            await self.handle_error(e, "member_update")


    # alert when a member has been "removed" from the server
    # no way to distinguish a kick or leave, only ban events
    async def member_remove(self, member: discord.Member):
        try:
           await self.say_to_channel(self.mod_chat, "User '{0}' has left the server.".format(member.name))
        except Exception as e:
            self.handle_error(e, "member_update")


    # update a member if they are streaming
    # so they are more visible to other users
    async def check_user_streaming(self, before: discord.Member, after: discord.Member) -> None:
        member_streaming = [r for r in after.roles if r.name == "streaming"]

        if after.game is not None and after.game.type == 1:
            if len(member_streaming) == 0:
                await self.bot.add_roles(after, self.role_streaming)

        elif before.game is not None and before.game.type == 1:
            if len(member_streaming) > 0:
                await self.bot.remove_roles(after, self.role_streaming)


    # make a basic http call
    # with urllib
    def http_get(self, url: str) -> json:
        try:
            return json.loads(urllib.request.urlopen(url).read())
        except Exception as e:
            self.handle_error(e, "http_get")


    # default catch for handling any errors that
    # occur when processing bot commands
    async def handle_error(self, error, command: str, say_error: bool = True) -> None:
        try:
            #if say_error:
                #await self.say("Ahh Error!")

            error_message: str = "Error occurred from command '{0}': {1}".format(command, error)
            traceback.print_exc(file=sys.stdout)

            await self.say_to_channel(self.bot_testing, error_message)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)


bunkbot = BunkBot()