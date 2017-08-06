"""
Commands only allowable by admin, moderator, and vip users
"""
from tinydb import Query
from discord import Member, Embed
from discord.ext import commands
from ..bunkbot import BunkBot
from src.storage.db import database

ALLOWABLE_SEARCH_PROPS = ["name", "nick", "display_name", "roles", "status"]
ALLOWABLE_DB_PROPS = []

class Mod:
    def __init__(self, bot: BunkBot):
        self.bot = bot


    # get info on a particular user
    # preferably their role(s) - otherwise
    # check names, nicks secondary - in channel?
    @commands.has_any_role("admin", "moderator")
    @commands.command(pass_context=True, cls=None, help="Retrieve user information")
    async def who(self, ctx):
        try:
            self.bot.send_typing(ctx)

            # i.e.   !who streaming
            # returns anyone who has 'streaming' role
            results = []
            param = self.bot.get_cmd_params(ctx)[0]

            for m in self.bot.server.members:
                member: Member = m
                for p in ALLOWABLE_SEARCH_PROPS:
                    val = getattr(member, p)
                    if str(val).lower() == param.lower():
                        msg = "Match: {0} ({1}) - {2}".format(member.name, p, str(val))

                        db_member = database.users.get(Query().name == member.name)

                        try:
                            if db_member is not None and db_member["last_online"] is not None:
                                msg += "  Last online {0}".format(db_member["last_online"])
                        except:
                            msg += "  No last online record"

                        results.append(msg)

            if len(results) > 0:
                embed = Embed(title="Query Results", description="\n".join(results))
                embed.set_footer(text="{0} results found".format(len(results)))
                await self.bot.say(embed=embed)
            else:
                await self.bot.say("No user retrieved with given query of '{0}'".format(param))

        except Exception as e:
            await self.bot.handle_error(e, "who")


def setup(bot: BunkBot):
    bot.add_cog(Mod(bot))