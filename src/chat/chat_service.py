from discord import Message, Member
from typing import List
from random import randint
from re import findall
from cleverwrap import CleverWrap

from .chat import Chat
from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_exception import BunkException
from ..core.bunk_user import BunkUser
from ..core.constants import DB_CLEVERBOT
from ..core.daemon import DaemonHelper
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
        self.chats: List[Chat] = []
        self.users: UserService = users
        self.channels: ChannelService = channels
        self.bot.on_initialized += self.setup_chat_helper
        #DaemonHelper.add(self.randomly_create_conversation, trigger="interval", hours=INTERVAL_FOR_RANDOM_CHAT)


    async def setup_chat_helper() -> None:
        chat_token = database.get(DB_CLEVERBOT)
        
        if chat_token is not None:
            self.chat_bot = CleverWrap(chat_token)
            self.bot.on_user_message += self.respond_to_message
        else:
            await self.channels.log_warning("Cleverbot token not supplied, BunkBot will be mute :(", "ChatService")


    # check for if the message sent by a user
    # is meant for bunkbot
    async def respond_to_message(self, message: Message) -> None:
        is_bunk_mention: bool = len(message.mentions) > 0 and message.mentions[0].name == "BunkBot"
        content: str = findall("[a-zA-Z]+", str(message.content).upper())

        if is_bunk_mention or "BUNKBOT" in content:
            await message.channel.send("Sorry, can't talk right now (I'm in rewrite mode)")
            return

            user: BunkUser = self.users.get_by_id(message.author.id)
            chat = next((c for c in self.chats if c.user.id == user.id), None)

            if chat is None:
                chat = Chat(user)
                self.chats.append(chat)

            if not chat.is_active:
                self.chats.remove(chat)
            else:
                pass
                #await message.channel.send(self.chat_bot.say(content))
        else:
            await self.bot.process_commands(message)


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
        