from random import randint
from discord.ext.commands import command, Context, Cog

from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_exception import BunkException
from ..core.bunk_user import BunkUser
from ..core.registry import CHANNEL_SERVICE, USER_SERVICE
from ..user.user_service import UserService


DESCRIPTION = """Basic one in six chance for a russian roulette"""

class Roulette(Cog):
    def __init__(self, channels: ChannelService, users: USER_SERVICE):
        self.channels: ChannelService = channels
        self.users: UserService = users


    @command(pass_context=True, cls=None, help=DESCRIPTION)
    async def roulette(self, ctx: Context) -> None:
        try:
            await ctx.trigger_typing()

            message: str = "Click..."
            user: BunkUser = self.users.get_by_id(ctx.message.author.id)

            bullet_location: int = randint(0, 5)
            if randint(0, 5) == bullet_location:
                message = "{0} :gun: BANG!!!!!!!!!".format(user.mention)

            await ctx.send(message)
        except Exception as e:
            await self.channels.log_error(e, "roll")


def setup(bot) -> None:
    bot.add_cog(Roulette(CHANNEL_SERVICE, USER_SERVICE))
