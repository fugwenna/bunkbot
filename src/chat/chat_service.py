from re import findall
from typing import List
from discord import Message

from .chat import Chat
from ..bunkbot import BunkBot
from ..core.service import Service
from ..db.database_service import DatabaseService

"""
Service responsible for dealing with
CleverBot and responding to
"""
class ChatService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService):
        super().__init__(bot, database)
        self.chats: List[Chat] = []
        self.bot.on_user_message += self.respond_to_message


    # check for if the message sent by a user
    # is meant for bunkbot
    async def respond_to_message(self, message: Message) -> None:
        #is_reset = str(message.content).strip() == "!reset"     
        is_bunk_mention: bool = len(message.mentions) > 0 and message.mentions[0].name == "BunkBot"
        content: str = findall("[a-zA-Z]+", str(message.content).upper())

        # todo .. is_chatting needs to be stateful
        #if not is_reset and (self.is_chatting or (is_bunk_mention or "BUNKBOT" in content)):
        if is_bunk_mention or "BUNKBOT" in content:
            await message.channel.send("Sorry, can't talk right now (I'm in rewrite mode)")
        else:
            await self.bot.process_commands(message)