"""
Discord.py wrapper class which inherits the
Bot class as it's parent
"""
import json, asyncio, re, sys, time, traceback, urllib.request
from urllib.request import HTTPError, URLError, socket
from os import walk
from os.path import join, splitext, sep
from discord import Channel, Member, Message, Reaction, Server, VoiceState, Embed, Role, Game, Status
from discord.ext.commands import Context
from cleverwrap import CleverWrap
from discord.ext import commands
from src.storage.db import database
from src.util.functions import to_name
from src.util.bunk_user import BunkUser
from src.util.bunk_exception import BunkException
from src.util.holidays import Holiday
from src.util.event_hook import EventHook
from src.util.constants import *
from src.util.helpers import roll, roll_int
from src.util.async import AsyncSchedulerHelper


BOT_DESCRIPTION = """
The bunkest bot - type '!help' for my commands, or say my name to chat with me. Type '!help [command] for more info
on a command (i.e. !help color)\n
"""


class BunkBot(commands.Bot):
    on_bot_initialized = EventHook()
    on_msg_received = EventHook()

    def __init__(self):
        super().__init__("!", None, BOT_DESCRIPTION, True)
        self.init: bool = False
        self.chat_timer = 9
        self.last_message_at = -1
        self.chat_bot: CleverWrap = None
        self.server: Server = None
        self.bot_testing: Channel = None
        self.bot_logs: Channel = None
        self.mod_chat: Channel = None
        self.general: Channel = None
        self.weather: Channel = None
        self.streams: Channel = None
        self.role_admin = None
        self.role_gaming = None
        self.role_streaming = None
        self.role_new = None
        self.role_vip = None
        self.role_vip_perms = None
        self.role_moderator = None
        self.role_moderator_perms = None
        self.role_bunky = None
        self.lowest_role_position: int = 0
        self.SERVER_LOCKED = False
        self.ADMIN: BunkUser = None
        self.MODERATORS: list = []
        self.BB_PROMPT: str = "tell me a fact"
        self.VIPS: list = []
        self.conversations = []
        self.users = []
        self.load_cogs()
        Holiday.on_holiday += self.send_greeting


    # lifecycle hook - set up all
    # of the necessary and useful channels
    async def on_init(self) -> None:
        try:
            if self.init is False:
                self.init = True
                self.server = self.get_server(database.get(DB_SERVER_ID))

                for ro in self.server.roles:
                    if ro.name == ROLE_STREAMING:
                        self.role_streaming = ro
                    elif ro.name == ROLE_GAMING:
                        self.role_gaming = ro
                    elif ro.name == ROLE_NEW:
                        self.role_new = ro
                        self.lowest_role_position = ro.position
                    elif ro.name == ROLE_ADMIN:
                        self.role_admin = ro
                    elif ro.name == ROLE_MODERATOR:
                        self.role_moderator = ro
                    elif ro.name == ROLE_MODERATOR_PERMS:
                        self.role_moderator_perms = ro
                    elif ro.name == ROLE_VIP:
                        self.role_vip = ro
                    elif ro.name == ROLE_VIP_PERMS:
                        self.role_vip_perms = ro
                    elif ro.name == ROLE_BUNKBOT:
                        self.role_bunky = ro

                for ch in self.server.channels:
                    if ch.name == CHANNEL_BOT_TESTING:
                        self.bot_testing = ch
                    elif ch.name == CHANNEL_BOT_LOGS:
                        self.bot_logs = ch
                    elif ch.name == CHANNEL_MOD_CHAT:
                        self.mod_chat = ch
                    elif ch.name == CHANNEL_GENERAL:
                        self.general = ch
                    elif ch.name == CHANNEL_WEATHER:
                        self.weather = ch
                    elif ch.name == CHANNEL_STREAMS:
                        self.streams = ch

                self.chat_bot = CleverWrap(database.get(DB_CLEVERBOT))
                await self.say_to_channel(self.bot_logs, "Bot and database initialized. Syncing users and channels...")
                await self.sync_users()
                await Holiday.start_timer()
                await BunkBot.on_bot_initialized.fire()
                await self.wire_random_game()
                await self.set_random_game(False)
        except Exception as e:
            await self.handle_error(e, "on_init")


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


    # member reference for
    # bunkbot to add roles
    @property
    def member_ref(self) -> Member or None:
        mem = [u for u in self.users if u.has_role(self.role_bunky)]
        if len(mem) > 0:
            return mem[0].member

        return None


    # check if bunkbot is chatting with
    # a specific bunk user
    def is_chatting_with(self, user: BunkUser) -> bool:
        return False


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
                if not member.bot:
                    user_added: bool = database.check_user_with_member(member)
                    if user_added:
                        await self.add_roles(member, self.role_new)
                        new_users.append(member.name)

                    user: BunkUser = BunkUser(member)
                    self.users.append(user)

                    if user.has_role(self.role_admin.name):
                        self.ADMIN = user
                    elif user.has_role(self.role_moderator.name):
                        self.MODERATORS.append(user)
                    elif user.has_role(self.role_vip.name):
                        self.VIPS.append(user)

                    await self.check_member_streaming(user, user)
                    await self.check_member_gaming(user, user)

            if len(new_users) > 0:
                new_user_list: str = "\n".join(new_users)
                new_user_msg: str = "Users synced. The following users have been added to the database: \n{0}".format(new_user_list)
                #await self.say_to_channel(self.mod_chat, new_user_msg)
            else:
                await self.say_to_channel(self.bot_logs, "Users synced. No new users added to database.")
        except Exception as e:
            await self.handle_error(e, "sync_users")


    # update bunkbot's random game every hour
    async def wire_random_game(self) -> None:
        try:
            AsyncSchedulerHelper.add_job(self.set_random_game, trigger="interval", minutes=60)
        except Exception as e:
            await self.handle_error(e, "wire_random_game")


    # annoy a random person during the day
    async def wire_annoy_someone(self) -> None:
        try:
            AsyncSchedulerHelper.add_job(self.annoy_someone, trigger="cron", hour=9)
        except Exception as e:
            await self.handle_error(e, "wire_annoy_someone")


    # process each message that is sent
    # to the server - if bunkbot is chatting, continue to chat
    # otherwise, process the message as a command
    async def process_message(self, message: Message) -> None:
        try:
            if message.author.bot:
                return

            bunk_user = self.get_user_by_id(message.author.id)

            is_reset = str(message.content).strip() == "!reset"
            is_bunk_mention = len(message.mentions) > 0 and message.mentions[0].name == "BunkBot"
            content = re.findall("[a-zA-Z]+", str(message.content).upper())

            if not is_reset and (self.is_chatting or (is_bunk_mention or "BUNKBOT" in content)):
                await self.chat(message)
                await bunk_user.update_xp(0.05, message.channel)
            else:
                await self.process_commands(message)
                await bunk_user.update_xp(1.0, message.channel)

            if is_reset:
                await self.delete_message(message)

            await BunkBot.on_msg_received.fire(message)

        except BunkException as be:
            await self.say_to_channel(self.bot_testing, be.message)
            await self.say_to_channel(self.bot_logs, message.content)
        except Exception as e:
            await self.handle_error(e, "process_message")


    # send a message to a random person 60% every day
    async def annoy_someone(self):
        try:
            pct = int(roll(1, 100))
            if pct >= 10:
                avail_mem_len = len([u for u in self.users if u.status == Status.online])
                if avail_mem_len > 0:
                    user: BunkUser = self.users[int(roll(0, avail_mem_len))]
                    # todo ignore list
                    await self.debug("Say something to " + user.name)
        except Exception as e:
            await self.handle_error(e, "annoy_someone")


    # send a message to a specific channel instead
    # of the normal channel of the message context object
    async def say_to_channel(self, channel: Channel, message: str or None, embed: Embed = None) -> Message:
        try:
            msg: Message = None
            self.send_typing(channel)

            if message is not None:
                msg = await self.send_message(channel, message)
            elif embed is not None:
                msg = await self.send_message(channel, None, embed=embed)

            return msg
        except Exception as e:
            await self.handle_error(e, "say_to_channel")


    # get a role based on the name
    async def get_role(self, role_name: str) -> Role or None:
        role = [r for r in self.server.roles if r == role_name]
        if len(role) > 0:
            return role[0]

        return None


    # have a cleverbot conversation with
    # a user if they say the name 'bunkbot'
    async def chat(self, message: Message) -> None:
        try:
            await self.send_typing(message.channel)
            content = re.sub(r'bunkbot', "", str(message.content), flags=re.IGNORECASE).strip()

            # if the user just says 'bunkbot'
            # treat it as a greeting
            if content == "":
                content = "Hello!"

            await self.send_message(message.channel, self.chat_bot.say(content))
            self.last_message_at = time.time()
        except Exception:
            await self.send_message(message.channel, "Sorry, I cannot talk right now :(")


    # greet a new member with a simple message,
    # apply the "new" role, and update the database
    async def member_join(self, member: Member) -> None:
        try:
            if self.SERVER_LOCKED:
                await self.kick(member)
                await self.say_to_channel(self.mod_chat, "User {0} kicked while joining during a server lock".format(member.name))
                return

            server: Server = member.server
            fmt: str = "Welcome {0.mention} to {1.name}!  Type !help for a list of my commands"

            database.check_user_with_member(member)
            self.users.append(BunkUser(member))
            await self.add_roles(member, self.role_new)

            await self.say_to_channel(self.mod_chat, "New user '{0}' has joined the server and added to the database".format(member.name))
            await self.send_message(server, fmt.format(member, server))
        except Exception as e:
            self.handle_error(e, "member_join")


    # perform custom functions when a user has
    # been updated - i.e. apply custom/temporary roles
    async def member_update(self, before: Member, after: Member) -> None:
        before_user = None
        bunk_user = None

        try:
            before_user: BunkUser = BunkUser(before)
            bunk_user: BunkUser = BunkUser(after)

        except BunkException as be:
            await self.say_to_channel(self.bot_testing, be.message)
        except Exception as e:
            await self.handle_error(e, "member_update")
            await self.say_to_channel(self.bot_logs, before.name)
            return

        await self.check_member_streaming(before_user, bunk_user)
        await self.check_member_gaming(before_user, bunk_user)
        await self.check_member_last_online(before_user, bunk_user)


    # alert when a member has been "removed" from the server
    # no way to distinguish a kick or leave, only ban events
    async def member_remove(self, member: Member) -> None:
        try:
           await self.say_to_channel(self.mod_chat, "@everyone :skull_crossbones: User '{0}' has left the server :skull_crossbones:".format(member.name))
        except Exception as e:
            self.handle_error(e, "member_update")


    # basic xp gains for various
    # events handled in main.py
    async def member_reaction_add(self, reaction: Reaction, member: Member) -> None:
        try:
            bunk_user: BunkUser = self.get_user_by_id(member.id)
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

            bunk_user: BunkUser = self.get_user_by_id(after.id)

            if bunk_user is not None:
                if is_voice or was_voice:
                    await bunk_user.update_xp(0.5)

        except BunkException as be:
            await self.say_to_channel(self.bot_testing, be.message)
        except Exception as e:
            await self.handle_error(e, "member_voice_update")


    # update a member if they are streaming
    # so they are more visible to other users
    async def check_member_streaming(self, before: BunkUser, after: BunkUser) -> None:
        try:
            bunk_user: BunkUser = self.get_user_by_id(after.id)

            if bunk_user is not None:
                if after.is_streaming and not bunk_user.has_role(self.role_streaming.name):
                    roles = after.roles.copy()
                    roles.append(self.role_streaming)

                    await bunk_user.update_xp(0.1)
                    #await self.add_roles(bunk_user.member, self.role_streaming)

                    if bunk_user.is_vip:
                        #await self.remove_roles(bunk_user.member, self.role_vip)
                        roles = [r for r in roles if r.name != self.role_vip.name]

                    if bunk_user.is_moderator:
                        #await self.remove_roles(bunk_user.member, self.role_moderator)
                        roles = [r for r in roles if r.name != self.role_moderator.name]

                    await self.bot.replace_roles(bunk_user.member, *roles)

                elif not after.is_streaming and before.is_streaming and bunk_user.has_role(self.role_streaming.name):
                    roles = [r for r in after.roles.copy() if r.name != self.role_streaming.name]

                    await bunk_user.update_xp(0.1)
                    #await self.remove_roles(bunk_user.member, self.role_streaming)

                    if bunk_user.is_vip:
                        roles.append(self.role_vip)
                        #await self.add_roles(bunk_user.member, self.role_vip)
                    elif bunk_user.is_moderator:
                        #await self.add_roles(bunk_user.member, self.role_moderator)
                        roles.append(self.role_moderator)

                    await self.bot.replace_roles(bunk_user.member, *roles)

        except BunkException as be:
            await self.say_to_channel(self.bot_testing, be.message)
        except Exception as e:
            await self.handle_error(e, "check_member_streaming")


    # check if a member is gaming and
    # add the 'gaming' role for whatever reason
    async def check_member_gaming(self, before: BunkUser, after: BunkUser) -> None:
        try:
            bunk_user: BunkUser = self.get_user_by_id(after.id)

            if bunk_user is not None:
                if after.is_gaming and not after.has_role(self.role_gaming.name):
                    await self.add_roles(bunk_user.member, self.role_gaming)
                elif not after.is_gaming and before.is_gaming and bunk_user.has_role(self.role_gaming.name):
                    await self.remove_roles(bunk_user.member, self.role_gaming)

                await self.sync_member_game(bunk_user)

        except BunkException as be:
            await self.say_to_channel(self.bot_testing, be.message)
        except Exception as e:
            await self.handle_error(e, "check_member_gaming")


    # update the users "last online"
    # property in the database
    async def check_member_last_online(self, before: BunkUser, after: BunkUser) -> None:
        try:
            pre_status = str(before.member.status)
            post_status = str(after.member.status)
            on_off = pre_status != "offline"and post_status == "offline"
            off_on = pre_status == "offline" and post_status != "offline"

            bunk_user: BunkUser = self.get_user_by_id(after.id)

            if bunk_user is not None:
                if on_off or off_on:
                    await bunk_user.update_last_online()

            if pre_status == "offline" and post_status == "idle":
                # invis?
                return
        except Exception as e:
            await self.handle_error(e, "check_member_last_online")


    # sync a members game with the database
    @staticmethod
    async def sync_member_game(user: BunkUser) -> None:
        if user.current_game is not None and user.current_game.type != 1:
            game_name = database.get_game_name(user.current_game.name)
            if game_name is None:
                database.game_names.insert({"name": user.current_game.name, "type": user.current_game.type})


    # get a member from the
    # collection of current members
    def get_user(self, name: str) -> BunkUser or None:
        nlower = to_name(name)

        for usr in self.users:
            mname = to_name(usr.name)

            if mname == nlower:
                return usr

        # no user found, raise exception
        raise BunkException("Cannot locate user {0}".format(name))


    # get a member from the
    # collection of current members
    def get_user_by_id(self, uid: str) -> BunkUser or None:
        for usr in self.users:
            if usr.id == uid:
                return usr

        # no user found, raise exception
        raise BunkException("Cannot locate user {0}".format(uid))


    # send a simple greeting to the
    # general chat channel
    async def send_greeting(self, message: str) -> None:
        try:
            await self.say_to_channel(self.general, message)
        except Exception as e:
            self.handle_error(e, "send_greeting")


    # check a game name with the database list
    # and randomly pick one
    async def set_random_game(self, roll_for_game: bool = True) -> None:
        if roll_for_game is True:
            roll_result = roll_int()
            if roll_result > 50:
                game = self.get_game()
                await self.change_presence(game=Game(name=game["name"], type=int(game["type"])))
        else:
            game = self.get_game()
            await self.change_presence(game=Game(name=game["name"], type=int(game["type"])))


    # get a game from the db
    @staticmethod
    def get_game() -> any:
        games = database.game_names.all()
        index = roll_int(0, len(games)-1)
        return games[index]


    # make a basic http call
    async def http_get(self, url: str) -> json:
        try:
            return json.loads(urllib.request.urlopen(url, timeout=1).read())
        except socket.timeout:
            await self.handle_error("http timeout", "http_get")
        except (HTTPError, URLError) as uhe:
            await self.handle_error(uhe, "http_get")
        except Exception as e:
            await self.handle_error(e, "http_get")


    # default catch for handling any errors that
    # occur when processing bot commands
    async def handle_error(self, error, command: str, ctx: Context = None) -> None:
        try:
            error_message: str = ":exclamation: Error occurred from command '{0}': {1}".format(command, error)

            if ctx is not None:
                msg: Message = ctx.message
                err: str = ":exclamation: An error has occurred! :exclamation: @fugwenna help ahhhh"
                await self.say_to_channel(msg.channel, err)

            await self.say_to_channel(self.bot_logs, error_message)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)


    # print debug messages to bot_testing
    async def debug(self, message: str) -> None:
        await self.say_to_channel(self.bot_logs, ":spider: {0}".format(message))


bunkbot = BunkBot()
