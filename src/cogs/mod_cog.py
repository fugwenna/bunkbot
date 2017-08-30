"""
Commands only allowable by admin, moderator, and vip users
"""
from tinydb import Query
from discord import Member, Embed
from discord.ext import commands
from discord.ext.commands import command
from ..bunkbot import BunkBot
from src.storage.db import database

ALLOWABLE_SEARCH_PROPS = ["name", "nick", "display_name", "roles", "status"]
ALLOWABLE_DB_PROPS = []

class Mod:
    def __init__(self, bot: BunkBot):
        self.bot = bot


    # link bunkbot source code
    @commands.has_any_role("admin")
    @command(pass_context=True, cls=None, help="Link source code url", aliases=["src"])
    async def source(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx)
            await self.bot.send_message(ctx.message.channel, "https://github.com/fugwenna/bunkbot/")
        except Exception as e:
            await self.bot.handle_error(e, "source")



    # clear a role for ALL users ...
    # be careful with this, basically an rm -rf
    @commands.has_any_role("admin")
    @command(pass_context=True, cls=None, help="Clear a role from all users")
    async def clear(self, ctx) -> None:
        try:
            param = self.bot.get_cmd_params(ctx)[0]
            role = [r for r in self.bot.server.roles if r.name == param][0]

            await self.bot.send_message(self.bot.mod_chat, "Clearing {0}...".format(param))
            for m in self.bot.server.members:
                await self.bot.remove_roles(m, role)

            await self.bot.send_message(self.bot.mod_chat, "Role {0} cleared from all users... good job idiot".format(param))

        except Exception as e:
            await self.bot.handle_error(e, "clear")



    # get info on a particular user
    # preferably their role(s) - otherwise
    # check names, nicks secondary - in channel?
    @commands.has_any_role("admin", "moderator")
    @command(pass_context=True, cls=None, help="Retrieve user information")
    async def who(self, ctx) -> None:
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