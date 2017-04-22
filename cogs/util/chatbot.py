from cleverwrap import CleverWrap
import re, time

"""
Slightly different bot that we do not register 
under the commands.ext, but new up manually under bot.py
"""
class Chatbot:
    def __init__(self, bot, token):
        self.bot = bot
        self.init = True
        self.chat_timer = 7
        self.last_message_at = -1
        self.clever_bot = CleverWrap(token)

    @property
    def is_chatting(self):
        if self.init:
            self.init = False
            return False

        if self.last_message_at == -1:
            return False

        new_time = time.time() - self.last_message_at 
        #new_seconds = new_time % 60

        still_chatting = new_time < self.chat_timer

        if not still_chatting:
            last_message_at = -1

        return still_chatting

    """
    Manually call
    the reply on messages
    """
    async def reply(self, message):
        try:
            await self.bot.send_typing(message.channel)
            content = str(message.content)
            if content == "":
                content = "hey"
                
            await self.bot.send_message(message.channel, self.clever_bot.say(content))
            self.last_message_at = time.time()
        except Exception as ex:
            print(ex)
            pass

    """
    Check if the bot is engaged in a question
    """
    def is_mention(self, message):
        content = str(message.content).upper().split(" ")
        is_bunk_mention = len(message.mentions) > 0 and message.mentions[0].name == "BunkBot"
        return is_bunk_mention or "BUNKBOT" in re.findall("[a-zA-Z]+", str(message.content).upper())
