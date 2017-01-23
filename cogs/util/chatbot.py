from cleverbot import Cleverbot
from .cog_wheel import CogWheel
import time

"""
Slightly different bot that we do not register 
under the commands.ext, but new up manually under bot.py
"""
class Chatbot:
    def __init__(self, bot):
        self.bot = bot
        self.init = True
        self.clever_bot = Cleverbot("Bunk Butter")
        self.chat_timer = 10 
        self.last_message_at = 0

    @property
    def is_chatting(self):
        if self.init:
            self.init = False
            return False

        new_time = time.time() - self.last_message_at 
        new_seconds = new_time % 60

        return new_seconds < self.chat_timer

    """
    Manually call
    the reply on messages
    """
    async def reply(self, message):
        await self.bot.send_typing(message.channel)
        await self.bot.send_message(message.channel, self.clever_bot.ask(str(message.content)))
        self.last_message_at = time.time()

    """
    Check if the bot is engaged in a question
    """
    def is_mention(self, message):
        content = str(message.content).upper().split(" ")
        is_bunk_mention = len(message.mentions) > 0 and message.mentions[0].name == "BunkBot"
        return is_bunk_mention or "BUNKBOT" in content
