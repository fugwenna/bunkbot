"""
Roll a random number
"""
from discord.ext.commands import command, Context
from src.bunkbot import BunkBot
from src.util.bunk_exception import BunkException
from src.util.bunk_user import BunkUser
from .hotslogs_result import HotslogsResult
from .hots_exception import HotsException

DESCRIPTION: str = """Commands for HOTS, using hotslogs.com data"""

class Hots:
    def __init__(self, bot: BunkBot):
        self.bot = bot

    # look up info on a hots player
    @command(pass_context=True, cls=None, help="Lookup a hots player based on name/id", aliases=["hp", "hotslogs", "hots"])
    async def hotsplayer(self, ctx: Context) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            cmds = self.bot.get_cmd_params(ctx)

            # assume the person is looking
            # up their profile, check the db
            # if they have on associated
            if len(cmds) == 0:
                await self.bot.say("Provide a player name or battle tag!")
                return

            data = None
            hrsult = HotslogsResult()
            identifier: str = cmds[0]

            # user has based an id
            if identifier.isdigit():
                data = hrsult.get_player_by_id(identifier)
            else:
                data = hrsult.get_player_by_name(identifier)


            print(data)

            #await self.bot.say(embed=Embed(title=title, description=message, color=ctx.message.author.color))

        except HotsException as he:
            await self.bot.say("Multiple players found for query: " + he.message)
        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "hotsplayer")


def setup(bot) -> None:
    bot.add_cog(Hots(bot))