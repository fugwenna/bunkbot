from random import randint
from discord.ext.commands import command, Context
from src.bunkbot import BunkBot
from src.util.bunk_exception import BunkException
from src.util.bunk_user import BunkUser

DESCRIPTION = """Basic one in six chance for a russian roulette"""

class Roulette:
    def __init__(self, bot: BunkBot):
        self.bot = bot

    @command(pass_context=True, cls=None, help=DESCRIPTION)
    async def roulette(self, ctx: Context) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            message = "Click..."
            user: BunkUser = self.bot.get_user_by_id(ctx.message.author.id)

            # chamber it
            bullet_location = randint(0, 5)

            # "spin" and fire it
            if randint(0, 5) == bullet_location:
                message = "{0} :gun: BANG!!!!!!!!!".format(user.mention)

            await self.bot.say(message)

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "roulette")


def setup(bot) -> None:
    bot.add_cog(Roulette(bot))