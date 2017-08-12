"""
RPG commands based on a user level
"""
from re import sub
from discord import Embed
from discord.ext import commands
from tinydb import Query
from src.bunkbot import BunkBot
from src.storage.db import database
from .rpg import rpg
from .duel import Duel


DUEL_DESCRIPTION = """Challenge a user to a duel. Type !duel <name> to challenge someone (i.e. !challenge fugwenna)
    \noptionally pass the max value that will be gambled in the duel (i.e. !challenge fugwenna 50 will challenge a user
     to a duel for 50 xp points.  Default is 10"""


class BunkRPG:
    def __init__(self, bot: BunkBot):
        self.bot = bot
        self.duels = []
        rpg.on_user_level += self.ding


    # DING - user has leveled up
    # inform them and update their server permissions
    async def ding(self, member, value):
        if member.name != "fugwenna":
            await self.bot.say_to_channel(self.bot.general, ":bell: DING! {0.mention} has advanced to level {1}!"
                                      .format(member, value))


    # allow users to print
    # out their current level
    @commands.command(pass_context=True, cls=None, help="Print your current level", aliases=["rank"])
    async def level(self, ctx):
        try:
            await self.bot.send_typing(ctx.message.channel)

            user = database.get_user(ctx.message.author)

            now_xp = user["xp"]
            prev_xp = rpg.calc_req_xp(user["level"])
            req_xp = rpg.calc_req_xp(user["level"] + 1)

            from_xp = round(now_xp - prev_xp, 2)
            to_xp = round(req_xp - prev_xp, 2)

            pct = from_xp / to_xp
            pct_rounded = int(round(pct, 1) * 10) * 3

            debug = "{0}, lvl {1} ({2}),   from:{3}-{4} ({5}/{6})"
            debug_msg = debug.format(user["name"], user["level"], now_xp, prev_xp, req_xp, from_xp, to_xp)
            await self.bot.send_message(self.bot.bot_testing, debug_msg)

            progress_bar = []
            for i in range(0, 29):
                progress_bar.append("--")

            for p in range(0, pct_rounded+1):
                progress_bar[p] = "#"

            member_name = str(ctx.message.author).split("#")[0]
            desc = "[{0}]".format("".join(progress_bar))

            embed = Embed(title="{0}: Level {1}".format(member_name, user["level"]), description=desc)
            embed.set_footer(text="You are currently {0}% to level {1}".format(round(pct * 100, 2), user["level"]+1))

            await self.bot.send_message(ctx.message.channel, embed=embed)
        except Exception as e:
            await self.bot.handle_error(e, "level")


    # get the top 10 leader board
    # sorting by level and xp
    @commands.command(pass_context=True, cls=None, help="Get the current leader board", aliases=["leaders", "ranks", "levels", "leaderboard"])
    async def leader(self, ctx):
        try:
            self.bot.send_typing(ctx.message.channel)

            players = sorted(filter(lambda u: u["name"] != "fugwenna", database.users.search(Query().xp > 1 or Query().xp > 0)),
                             key=lambda x: (x["level"], x["xp"]), reverse=True)[:9]

            board = ""
            for p in players:
                board += "{0}   level: {1}   xp: {2}/{3}\n".format(p["name"], p["level"],
                                                                round(p["xp"], 2),
                                                                rpg.calc_req_xp(p["level"]+1))

            embed = Embed(title="Leader board", description=board)

            await self.bot.send_message(ctx.message.channel, embed=embed)
        except Exception as e:
            await self.bot.handle_error(e, "leaders")


    # challenge another user
    # to an XP duel!
    @commands.command(pass_context=True, cls=None, help=DUEL_DESCRIPTION, aliases=["challenge"])
    async def duel(self, ctx):
        try:
            challenger = ctx.message.author
            challenger_name = str(ctx.message.author).split("#")[0]
            param = self.bot.get_cmd_params(ctx)

            if len(param) == 0:
                await self.bot.send_message(ctx.message.channel, "You must supply a challenger!")
                return

            opponent = " ".join(param[0:])

            if challenger_name == opponent:
                await self.bot.send_message(ctx.message.channel, "You can't challenge yourself to a duel, loser")
                return

            member = await self.bot.get_member(opponent)

            if member is None:
                await self.bot.send_message(ctx.message.channel, "User {0} not found".format(opponent))
                return

            c_dueling = [d for d in self.duels if d.challenger == challenger_name or d.challenger == opponent]
            o_dueling = [d for d in self.duels if d.opponent == opponent or d.opponent == challenger_name]

            if c_dueling:
                await self.bot.send_message(ctx.message.channel, "{0} is currently dueling".format(challenger_name))
                return

            if o_dueling:
                await self.bot.send_message(ctx.message.channel, "{0} is currently dueling".format(opponent))
                return

            self.duels.append(Duel(challenger, member))

            await self.bot.send_message(ctx.message.channel,
                                        ":triangular_flag_on_post: {0.mention} is challenging {1.mention} to a duel! Type !accept to duel, or !reject to run away like a little biiiiiiiiiiiiitch"
                                        .format(ctx.message.author, member))
        except Exception as e:
            await self.bot.handle_error(e, "challenge")


    # accept a duel!
    @commands.command(pass_context=True, cls=None, help="Accept a duel")
    async def accept(self, ctx):
        try:
            name = str(ctx.message.author).split("#")[0]

            for d in self.duels:
                if d.opponent.name == name:
                    #todo TMP
                    self.duels.remove(d)
                    await self.bot.send_message(ctx.message.channel, ":crossed_swords: Coming Soon! Fugwenna is a lazy bastard.")
                    return

            await self.bot.send_message(ctx.message.channel, "You have no duels to accept")
        except Exception as e:
            await self.bot.handle_error(e, "accept")


    # reject a duel
    @commands.command(pass_context=True, cls=None, help="Reject a duel")
    async def reject(self, ctx):
        try:
            name = str(ctx.message.author).split("#")[0]

            for d in self.duels:
                if d.opponent.name == name:
                    self.duels.remove(d)
                    await self.bot.send_message(ctx.message.channel, ":exclamation: {0.mention} has rejected a duel with {1.mention}".format(d.opponent, d.challenger))
                    return

            await self.bot.send_message(ctx.message.channel, "You have no duels to reject")
        except Exception as e:
            await self.bot.handle_error(e, "cancel")


    # cancel a duel
    @commands.command(pass_context=True, cls=None, help="Cancel a duel")
    async def cancel(self, ctx):
        try:
            name = str(ctx.message.author).split("#")[0]

            for d in self.duels:
                if d.challenger == ctx.message.author:
                    self.duels.remove(d)
                    await self.bot.send_message(ctx.message.channel, "{0} has cancelled their duel with {0.mention}".format(name, d.opponent))
                    return

            await self.bot.send_message(ctx.message.channel, "You have no duels to cancel")
        except Exception as e:
            await self.bot.handle_error(e, "cancel")

def setup(bot) -> None:
    bot.add_cog(BunkRPG(bot))