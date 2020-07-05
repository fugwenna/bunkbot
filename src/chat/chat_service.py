from cleverwrap import CleverWrap
from discord import Message, Member
from typing import List
from random import randint
from re import findall
from string import punctuation

from .chat import Chat
from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_exception import BunkException
from ..core.bunk_user import BunkUser
from ..core.daemon import DaemonHelper
from ..core.functions import get_cmd_params, will_execute_on_chance
from ..core.service import Service
from ..db.database_service import DatabaseService
from ..user.user_service import UserService


INTERVAL_FOR_RANDOM_CHAT: int = 3


"""
Service responsible for dealing with
CleverBot and responding to
"""
class ChatService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService, users: UserService, channels: ChannelService):
        super().__init__(bot, database)
        self.chat_bot: CleverWrap = None
        self.chats: List[Chat] = []
        self.users: UserService = users
        self.channels: ChannelService = channels
        self.bot.on_initialized += self.setup_chat_helper
        self.config.raise_error_on_bad_config = False
        #DaemonHelper.add(self.randomly_create_conversation, trigger="interval", hours=INTERVAL_FOR_RANDOM_CHAT)


    async def setup_chat_helper(self) -> None:
        chat_token = self.config.cleverbot_api_key
        
        if chat_token is not None:
            self.chat_bot = CleverWrap(chat_token, self.bot.name)
            self.bot.on_user_message += self.respond_to_message
        else:
            await self.channels.log_warning("Cleverbot token not supplied, BunkBot will be mute :(")


    # check for if the message sent by a user
    # is meant for bunkbot
    async def respond_to_message(self, message: Message) -> None:
        if not message.author.bot:
            if message.content.startswith("!"):
                await self.bot.process_commands(message)
            else:
                user: BunkUser = self.users.get_by_id(message.author.id)
                chat: Chat = next((c for c in self.chats if c.user.id == user.id and c.channel_id == message.channel.id), None)
                is_bunk_mention: bool = len(message.mentions) > 0 and message.mentions[0].name == self.bot.name
                parsed_chat: list = Chat.parse(message.content)
                bunk_name_index: int = -1

                try:
                    bunk_name_index = parsed_chat.index(self.bot.name_lower)
                except:
                    bunk_name_index = -1

                if is_bunk_mention or bunk_name_index > -1:
                    if chat is None:
                        chat = Chat(user, message)
                        self.chats.append(chat)

                    is_first = bunk_name_index == 0
                    is_last = bunk_name_index == len(parsed_chat)-1
                    is_one_time_response = not is_first and not is_last
                    will_respond: bool = True

                    if is_one_time_response:
                        will_respond = randint(0, 100) >= 50

                    if will_respond:
                        await self.respond(chat, message, user)
                        if is_one_time_response:
                            chat.last_message_at = -1
                            self.chats.remove(chat)
                else:
                    if chat is not None and chat.channel_id == message.channel.id:
                        if chat.is_active:
                            if message.content.lower() == "quiet":
                                chat.last_message_at = -1
                                self.chats.remove(chat)
                                await message.channel.send(":face_with_hand_over_mouth:")
                            else:
                                await self.respond(chat, message, user)
                        else:
                            self.chats.remove(chat)
                    else:
                        await self.bot.process_commands(message)


    async def respond(self, chat: Chat, message: Message, user: BunkUser) -> None:
        try:
            await message.channel.trigger_typing()
            content: str = self.override(message)

            response: str = self.chat_bot.say(chat.reply(content, user))
            response = self.alter_response(user, response)

            self.update_inactive_chats()

            await message.channel.send(response)
        except Exception as e:
            await self.channels.log_error(e, "ChatService")
            await message.channel.send("I'm sorry... I cannot talk right now")


    def alter_response(self, user: BunkUser, response: str) -> str:
        if not response[-1] in punctuation:
            return response

        if len(self.chats) > 1 and will_execute_on_chance(80):
             response = "{0}, {1}{2}".format(response[:-1], user.name, response[-1])

        return response


    # every 3 hours, random decide to ping someone (with an exclude list)
    # who is online and not gaming
    async def randomly_create_conversation(self) -> None:
        users: List[BunkUser] = []

        for member in self.bot.server.members:
            user: BunkUser = self.users.get_by_id(member.id)

            if user is not None and user.is_online and not user.is_gaming:
                print("SNAG EM {0}".format(user.name))
                users.append(user)
            
        user: BunkUser = users[randint(0, len(users)-1)]


    def update_inactive_chats(self) -> None:
        for chat in self.chats:
            if not chat.check_if_active():
                self.chats.remove(chat)
        

    # "override" commands for bunkbot
    @staticmethod
    def override(msg: Message) -> bool:
        content: str = msg.content.split()[0]
        if content == "!duel":
            return "Duel me you coward!"

        return msg.content