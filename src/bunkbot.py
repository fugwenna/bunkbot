"""
Discord.py wrapper class which inherits the
Bot class as it's parent
"""
import json
import re
import sys
import time
import traceback
import urllib.request
from re import sub
from os import walk
from os.path import join, splitext, sep
from discord import Channel, Member, Message, Reaction, Server, VoiceState, Embed
from cleverwrap import CleverWrap
from discord.ext import commands
from src.storage.db import database
from src.util.helpers import USER_NAME_REGEX
from src.util.bunk_user import BunkUser
from src.util.bunk_exception import BunkException
from src.util.holidays import Holiday
from src.util.event_hook import EventHook


BOT_DESCRIPTION = """
The bunkest bot - type '!help' for my commands, or say my name to chat with me. Type '!help [command] for more info
on a command (i.e. !help color)\n
"""

class BunkBot(commands.Bot):
    on_bot_initialized = EventHook()

    def __init__(self):
        super().__init__("!", None, BOT_DESCRIPTION, False)
        self.init: bool = False
        self.chat_timer = 9
        self.last_message_at = -1
        self.chat_bot: CleverWrap = None
        self.server: Server = None
        self.bot_testing: Channel = None
        self.bot_logs: Channel = None
        self.mod_chat: Channel = None
        self.vip_chat: Channel = None
        self.general: Channel = None
        self.role_streaming = None
        self.role_new = None
        self.role_vip = None
        self.role_moderator = None
        self.users = []
        self.load_cogs()
        Holiday.on_holiday += self.send_greeting


    # lifecycle hook - set up all
    # of the necessary and useful channels
    async def on_init(self):
        if self.init is False:
            self.init = True
            self.server = self.get_server(database.get("serverid"))

            for ro in self.server.roles:
                if ro.name == "streaming":
                    self.role_streaming = ro
                elif ro.name == "new":
                    self.role_new = ro
                elif ro.name == "moderator":
                    self.role_moderator = ro
                elif ro.name == "vip":
                    self.role_vip = ro

            for ch in self.server.channels:
                if ch.name == "bot-testing":
                    self.bot_testing = ch
                elif ch.name == "bot-logs":
                    self.bot_logs = ch
                elif ch.name == "mod-chat":
                    self.mod_chat = ch
                elif ch.name == "vip-chat":
                    self.vip_chat = ch
                elif ch.name == "general":
                    self.general = ch

            self.chat_bot = CleverWrap(database.get("cleverbot"))
            await self.say_to_channel(self.bot_logs, "Bot and database initialized. Syncing users and channels...")
            await self.sync_users()
            await Holiday.start_timer()
            await BunkBot.on_bot_initialized.fire()


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
    def is_chatting(self) -> bool:
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
                    await self.add_roles(member, self.role_new)
                    new_users.append(member.name)

                user: BunkUser = BunkUser(member)
                self.users.append(user)
                await self.check_member_streaming(user, user)

            if len(new_users) > 0:
                new_user_list: str = "\n".join(new_users)
                new_user_msg: str = "Users synced. The following users have been added to the database: \n{0}".format(new_user_list)
                await self.say_to_channel(self.mod_chat, new_user_msg)
            else:
                await self.say_to_channel(self.bot_logs, "Users synced. No new users added to database.")
        except Exception as e:
            await self.handle_error(e, "sync_users")

    # process each message that is sent
    # to the server - if bunkbot is chatting, continue to chat
    # otherwise, process the message as a command
    async def process_message(self, message: Message) -> None:
        try:
            if message.author.bot:
                return

            bunk_user = self.get_user(message.author.name)

            is_reset = str(message.content).strip() == "!reset"
            is_bunk_mention = len(message.mentions) > 0 and message.mentions[0].name == "BunkBot"
            content = re.findall("[a-zA-Z]+", str(message.content).upper())

            if not is_reset and (self.is_chatting or (is_bunk_mention or "BUNKBOT" in content)):
                await self.chat(message)
                await bunk_user.update_xp(0.5, message.channel)
            else:
                await self.process_commands(message)
                await bunk_user.update_xp(1.0, message.channel)

            if is_reset:
                await self.delete_message(message)

        except BunkException as be:
            await self.say_to_channel(self.bot_testing, be.message)
        except Exception as e:
            await self.handle_error(e, "process_message")


    # send a message to a specific channel instead
    # of the normal channel of the message context object
    async def say_to_channel(self, channel: Channel, message: str or None, embed: Embed = None) -> None:
        try:
            self.send_typing(channel)

            if message is not None:
                await self.send_message(channel, message)
            elif embed is not None:
                await self.send_message(channel, None, embed=embed)
        except Exception as e:
            await self.handle_error(e, "say_to_channel")


    # have a cleverbot conversation with
    # a user if they say the name 'bunkbot'
    async def chat(self, message: Message) -> None:
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
    async def member_join(self, member: Member) -> None:
        try:
            server: Server = member.server
            fmt: str = "Welcome {0.mention} to {1.name}!  Type !help for a list of my commands"

            database.check_user(member)
            self.users.append(BunkUser(member))
            await self.add_roles(member, self.role_new)

            await self.say_to_channel(self.mod_chat, "New user '{0}' has joined the server and added to the database".format(member.name))
            await self.send_message(server, fmt.format(member, server))
        except Exception as e:
            self.handle_error(e, "member_join")


    # perform custom functions when a user has
    # been updated - i.e. apply custom/temporary roles
    async def member_update(self, before: Member, after: Member) -> None:
        try:
            before_user: BunkUser = BunkUser(before)
            bunk_user: BunkUser = BunkUser(after)

            await self.check_member_streaming(before_user, bunk_user)
            await self.check_member_last_online(before_user, bunk_user)

        except BunkException as be:
            await self.say_to_channel(self.bot_testing, be.message)
        except Exception as e:
            await self.handle_error(e, "member_update")


    # alert when a member has been "removed" from the server
    # no way to distinguish a kick or leave, only ban events
    async def member_remove(self, member: Member) -> None:
        try:
           await self.say_to_channel(self.mod_chat, "@everyone User '{0}' has left the server.".format(member.name))
        except Exception as e:
            self.handle_error(e, "member_update")


    # basic xp gains for various
    # events handled in main.py
    async def member_reaction_add(self, reaction: Reaction, member: Member) -> None:
        try:
            bunk_user: BunkUser = self.get_user(member.name)
            await bunk_user.update_xp(0.15)


        except BunkException as be:
            await self.say_to_channel(self.bot_testing, be.message)
        except Exception as e:
            await self.handle_error(e, "member_reaction_add")


    # give a slight xp increase
    # when a user joins a voice channel
    async def member_voice_update(self, before: Member, after: Member) -> None:
        try:
            before_voice: VoiceState = before.voice.voice_channel
            after_voice: VoiceState = after.voice.voice_channel

            is_voice = before_voice is None and after_voice is not None
            was_voice = before_voice is not None and after_voice is None

            bunk_user: BunkUser = self.get_user(after.name)

            if is_voice or was_voice:
                await bunk_user.update_xp(0.5)

        except BunkException as be:
            await self.say_to_channel(self.bot_testing, be.message)
        except Exception as e:
            await self.handle_error(e, "member_voice_update")
            await self.say_to_channel(self.bot_logs, traceback.print_exc(file=sys.stdout))


    # update a member if they are streaming
    # so they are more visible to other users
    async def check_member_streaming(self, before: BunkUser, after: BunkUser) -> None:
        try:
            bunk_user: BunkUser = self.get_user(after.name)

            if bunk_user is not None:
                # if after.is_streaming:
                if after.member.game is not None and after.member.game.type == 1:
                    await self.debug("{0} is now streaming...".format(after.name))
                    await self.debug("checking custom role " + str(after.is_streaming))
                    await self.debug("has role?" + str(after.has_role(self.role_streaming)))
                    if len([r for r in after.member.roles if r.name == self.role_streaming.name]) == 0:
                    #if not after.has_role(self.role_streaming):
                        await self.debug("adding xp")
                        await bunk_user.update_xp(0.1)
                        await self.debug("adding role")
                        await self.add_roles(after.member, self.role_streaming)
                #elif before.is_streaming:
                elif before.member.game is not None and before.member.game.type == 1:
                    self.debug("{0} is not streaming".format(before.name))
                    self.debug("checking custom role " + str(before.is_streaming))
                    self.debug("has role?" + str(after.has_role(self.role_streaming)))
                    if len([r for r in after.member.roles if r.name == self.role_streaming.name]) > 0:
                    #if after.has_role(self.role_streaming):
                        await self.debug("adding xp")
                        await bunk_user.update_xp(0.1)
                        await self.debug("removing role")
                        await self.remove_roles(after.member, self.role_streaming)

        except BunkException as be:
            await self.say_to_channel(self.bot_testing, be.message)
        except Exception as e:
            print(e)


    # update the users "last online"
    # property in the database
    async def check_member_last_online(self, before: BunkUser, after: BunkUser) -> None:
        pre_status = str(before.member.status)
        post_status = str(after.member.status)
        on_off = pre_status != "offline"and post_status == "offline"
        off_on = pre_status == "offline" and post_status != "offline"

        bunk_user: BunkUser = self.get_user(after.name)

        if on_off or off_on:
            await bunk_user.update_last_online()

        if pre_status == "offline" and post_status == "idle":
            # from 'invisible' ...
            return


    # get a member from the
    # collection of current members
    def get_user(self, user: str or Member) -> BunkUser or None:
        name: str = user

        if type(user) is Member:
            name = user.name

        nlower = sub(USER_NAME_REGEX, "", name.lower().strip())

        for usr in self.users:
            mname = sub(USER_NAME_REGEX, "", usr.name.lower().strip())

            if mname == nlower:
                return usr
            elif usr.member.display_name is not None:
                dname = sub(USER_NAME_REGEX, "", usr.member.display_name.lower().strip())
                if dname == nlower:
                    return usr
            elif usr.member.nick is not None:
                nick = sub(USER_NAME_REGEX, "", usr.member.nick.lower().strip())
                if nick == nlower:
                    return usr

        # no user found, raise exception
        raise BunkException("Cannot locate user {0}".format(name))


    # send a simple greeting to the
    # general chat channel
    async def send_greeting(self, message: str) -> None:
        try:
            await self.debug("Testing cron task events...")
            await self.debug(message)
        except Exception as e:
            self.handle_error(e, "send_greeting")


    # make a basic http call
    # with urllib
    def http_get(self, url: str) -> json:
        try:
            return json.loads(urllib.request.urlopen(url).read())
        except Exception as e:
            self.handle_error(e, "http_get")


    # default catch for handling any errors that
    # occur when processing bot commands
    async def handle_error(self, error, command: str) -> None:
        try:
            error_message: str = ":exclamation: Error occurred from command '{0}': {1}".format(command, error)

            try:
                await self.say_to_channel(traceback.print_exc(file=sys.stdout))
            except:
                await self.say_to_channel(self.bot_logs, "Error printing traceback")
                pass

            await self.say_to_channel(self.bot_logs, error_message)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)


    # print debug messages to bot_testing
    async def debug(self, message: str) -> None:
        await self.say_to_channel(self.bot_logs, ":spider: {0}".format(message))


bunkbot = BunkBot()
