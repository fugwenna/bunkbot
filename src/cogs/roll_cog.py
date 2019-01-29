from discord import Embed
from discord.ext.commands import command, Context
from ..bunkbot import BunkBot
from ..models.bunk_user import BunkUser
from ..services.user_service import UserService
from ..services.channel_service import ChannelService
from ..util.registry import USER_SERVICE, CHANNEL_SERVICE

ROLE_DESCRIPTION = """Roll a random value between 0 and 100.  Optionally, you may pass a value range.\n
    Example: !roll
    Example: !roll 1-10
"""
class Roll:
    def __init__(self, channels: ChannelService, users: UserService):
        self.channels: ChannelService = channels
        self.users: UserService = users

    # roll a random number
    # optionally specify a value range with default 0-100
    @command(pass_context=True, help=ROLE_DESCRIPTION)
    async def roll(self, ctx: Context) -> None:
        try:
            await self.channels.type(ctx)

            min_val = 0
            max_val = 100
            params = self.bot.get_cmd_params(ctx)
            user: BunkUser = self.users.get(ctx.message.author.id)

            if len(params) > 0:
                if "-" in params[0]:
                    p_split = params[0].split("-")
                    if p_split[0].isdigit() and p_split[1].isdigit():
                        val_1 = int(p_split[0])
                        val_2 = int(p_split[1])
                        min_val = val_1 if val_1 <= val_2 else val_2
                        max_val = val_1 if val_2 <= val_1 else val_2

            title = "Rolling ({0}-{1})".format(min_val, max_val)
            message = "{0} rolls {1}".format(user.name, str(randint(min_val, max_val)))

            #await self.bot.say(embed=Embed(title=title, description=message, color=ctx.message.author.color))
        except Exception as e:
            await self.bot.handle_error(e, "roll")


def setup(bot: BunkBot) -> None:
    bot.add_cog(Roll(CHANNEL_SERVICE, USER_SERVICE))
