"""
Commands only allowable by admin and moderator
"""
from discord.ext import commands
from discord.ext.commands import command, Context
from src.bunkbot import BunkBot

ALLOWABLE_SEARCH_PROPS = ["name", "nick", "display_name", "roles", "status"]
ALLOWABLE_DB_PROPS = []

class Mod:
    def __init__(self, bot: BunkBot):
        self.bot: BunkBot = bot


    # unlock the server and do not allow invitations
    @commands.has_any_role("admin", "moderator")
    @command(pass_context=True, cls=None, help="Lock the server")
    async def lock(self, ctx: Context) -> None:
        self.bot.SERVER_LOCKED = True
        await self.bot.say_to_channel(self.bot.mod_chat, ":shield: SERVER UNLOCKED :shield: Invited members will be automatically kicked")

        if ctx.message.channel != self.bot.mod_chat:
            await self.bot.delete_message(ctx.message)


    # unlock the server and allow invitations
    @commands.has_any_role("admin", "moderator")
    @command(pass_context=True, cls=None, help="Unlock the server")
    async def lock(self, ctx: Context) -> None:
        self.bot.SERVER_LOCKED = False
        await self.bot.say_to_channel(self.bot.mod_chat, "SERVER UNLOCKED: Invitations allowed")

        if ctx.message.channel != self.bot.mod_chat:
            await self.bot.delete_message(ctx.message)


    # # get info on a particular user
    # # preferably their role(s) - otherwise
    # # check names, nicks secondary - in channel?
    # # this command kinda sucks
    # @commands.has_any_role("admin", "moderator")
    # @command(pass_context=True, cls=None, help="Retrieve user information")
    # async def who(self, ctx) -> None:
    #     try:
    #         self.bot.send_typing(ctx)
    #
    #         # i.e.   !who streaming
    #         # returns anyone who has 'streaming' role
    #         results = []
    #         param = self.bot.get_cmd_params(ctx)[0]
    #
    #         for m in self.bot.server.members:
    #             member: Member = m
    #             for p in ALLOWABLE_SEARCH_PROPS:
    #                 val = getattr(member, p)
    #                 if str(val).lower() == param.lower():
    #                     msg = "Match: {0} ({1}) - {2}".format(member.name, p, str(val))
    #
    #                     db_member = database.users.get(Query().name == member.name)
    #
    #                     try:
    #                         if db_member is not None and db_member["last_online"] is not None:
    #                             msg += "  Last online {0}".format(db_member["last_online"])
    #                     except:
    #                         msg += "  No last online record"
    #
    #                     results.append(msg)
    #
    #         if len(results) > 0:
    #             embed = Embed(title="Query Results", description="\n".join(results))
    #             embed.set_footer(text="{0} results found".format(len(results)))
    #             await self.bot.say(embed=embed)
    #         else:
    #             await self.bot.say("No user retrieved with given query of '{0}'".format(param))
    #
    #     except Exception as e:
    #         await self.bot.handle_error(e, "who")


def setup(bot: BunkBot):
    bot.add_cog(Mod(bot))