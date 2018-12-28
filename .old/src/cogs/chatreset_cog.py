"""
Tell bunkbot to shut his god damn mouth
"""
from discord.ext.commands import command
from ..bunkbot import BunkBot

class ChatReset:
    def __init__(self, bot: BunkBot):
        self.bot = bot


    # reset the last_message_at command for bunkbot
    @command(pass_context=False, cls=None, help="Reset BunkBot's chat so he shuts his ridiculous mouth")
    async def reset(self) -> None:
        self.bot.last_message_at = -1


def setup(bot: BunkBot) -> None:
    bot.add_cog(ChatReset(bot))