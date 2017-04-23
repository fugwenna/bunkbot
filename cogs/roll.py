from random import randint
from discord.ext import commands
from .util.cog_wheel import CogWheel

HELP_DESCRIPTION = """Roll a random value between 0 and 100.  Optionally, you may pass a value range.\n
    Example: !roll
    Example: !roll 1-10
"""

class Roll(CogWheel):
    def __init__(self, bot):
        CogWheel.__init__(self, bot)

    @commands.command(pass_context=True, cls=None, help=HELP_DESCRIPTION)
    async def roll(self, ctx):
        min_val = 0
        max_val = 100
        params = self.get_cmd_params(ctx)

        if len(params) > 0:
            if "-" in params[0]:
                psplit = params[0].split("-")
                if psplit[0].isdigit() and psplit[1].isdigit():
                    val_1 = int(psplit[0])
                    val_2 = int(psplit[1])
                    min_val = val_1 if val_1 <= val_2 else val_2
                    max_val = val_1 if val_2 <= val_1 else val_2

        
        title = "Rolling ({0}-{1})".format(min_val, max_val)
        message = "{0} rolls {1}".format(self.get_author(ctx), str(randint(min_val, max_val)))

        await self.send_message(title, message)


def setup(bot):
    bot.add_cog(Roll(bot))
