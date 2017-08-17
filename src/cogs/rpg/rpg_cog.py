"""
RPG commands based on a user level
"""
from re import sub
from discord import Embed
from discord.ext import commands
from tinydb import Query
from src.bunkbot import BunkBot
from src.util.bunk_user import BunkUser
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
    async def ding(self, member, value) -> None:
        if member.name != "fugwenna":
            await self.bot.say_to_channel(self.bot.general, ":bell: DING! {0.mention} has advanced to level {1}!"
                                      .format(member, value))


    # allow users to print
    # out their current level
    # todo - use BunkUser
    @commands.command(pass_context=True, cls=None, help="Print your current level", aliases=["rank"])
    async def level(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            user: BunkUser = self.bot.get_user_by_name(ctx.message.author.name)
            color = ctx.message.author.color

            params = self.bot.get_cmd_params(ctx)
            if len(params) > 0:
                param_user: BunkUser = self.bot.get_user_by_name(params[0])
                if param_user is None:
                    await self.bot.say("Cannot locate user '{0}'".format(params[0]))
                    return

                user = param_user
                color = param_user.member.color

            now_xp = user.xp
            prev_xp = rpg.calc_req_xp(user.level)
            req_xp = rpg.calc_req_xp(user.next_level)

            from_xp = round(now_xp - prev_xp, 2)
            to_xp = round(req_xp - prev_xp, 2)

            pct = from_xp / to_xp
            pct_rounded = int(round(pct, 1) * 10) * 2

            progress_bar = []
            for i in range(0, 20):
                progress_bar.append("▯")

            for p in range(0, pct_rounded-1):
                progress_bar[p] = "▮"

            desc = "{0}".format("".join(progress_bar))

            embed = Embed(title="{0}: Level {1}".format(user.name, user.level), description=desc, color=color)

            if len(params) > 0:
                embed.set_footer(
                    text="{0} is currently {1}% to level {2}"
                        .format(user.name, round(pct * 100, 2), user.next_level))
            else:
                embed.set_footer(text="You are currently {0}% to level {1}".format(round(pct * 100, 2), user.next_level))

            await self.bot.send_message(ctx.message.channel, embed=embed)
        except Exception as e:
            await self.bot.handle_error(e, "level")


    # get the top 10 leader board
    # sorting by level and xp
    # todo - use bot.users ?
    @commands.command(pass_context=True, cls=None, help="Get the current leader board", aliases=["leaders", "ranks", "levels", "leaderboard"])
    async def leader(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            players = sorted(filter(lambda u: u["name"] != "fugwenna", database.users.search(Query().xp > 1 or Query().xp > 0)),
                             key=lambda x: (x["level"], x["xp"]), reverse=True)[:9]

            names = []
            levels = []
            xps = []

            for p in players:
                names.append(sub(r"[^A-Za-z]+", "", p["name"]))
                levels.append(str(p["level"]))
                xps.append(str(p["xp"]))

            embed = Embed(title="", color=int("19CF3A", 16))
            embed.add_field(name="Name", value="\n".join(names), inline=True)
            embed.add_field(name="Level", value="\n".join(levels), inline=True)
            embed.add_field(name="Total XP", value="\n".join(xps), inline=True)

            await self.bot.send_message(ctx.message.channel, embed=embed)
        except Exception as e:
            await self.bot.handle_error(e, "leaders")


    # challenge another user
    # to an XP duel!
    @commands.command(pass_context=True, cls=None, help=DUEL_DESCRIPTION, aliases=["challenge"])
    async def duel(self, ctx) -> None:
        try:
            challenger = ctx.message.author
            challenger_name = str(ctx.message.author).split("#")[0]
            param = self.bot.get_cmd_params(ctx)

            if len(param) == 0:
                await self.bot.send_message(ctx.message.channel, "You must supply a challenger!")
                return

            opponent: str = " ".join(param[0:])

            if challenger_name == opponent:
                await self.bot.send_message(ctx.message.channel, "You can't challenge yourself to a duel, loser")
                return

            user: BunkUser = self.bot.get_user_by_name(opponent)

            if user is None:
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

            self.duels.append(Duel(challenger, user))

            await self.bot.send_message(ctx.message.channel,
                                        ":triangular_flag_on_post: {0.mention} is challenging {1.mention} to a duel! Type !accept to duel, or !reject to run away like a little biiiiiiiiiiiiitch"
                                        .format(ctx.message.author, user))
        except Exception as e:
            await self.bot.handle_error(e, "challenge")


    # accept a duel!
    @commands.command(pass_context=True, cls=None, help="Accept a duel")
    async def accept(self, ctx) -> None:
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
    async def reject(self, ctx) -> None:
        try:
            name = str(ctx.message.author).split("#")[0]

            for d in self.duels:
                if d.opponent.name == name:
                    self.duels.remove(d)
                    await self.bot.send_message(ctx.message.channel, ":exclamation: {0} has rejected a duel with {1.mention}".format(d.opponent, d.challenger))
                    return

            await self.bot.send_message(ctx.message.channel, "You have no duels to reject")
        except Exception as e:
            await self.bot.handle_error(e, "cancel")


    # cancel a duel
    @commands.command(pass_context=True, cls=None, help="Cancel a duel")
    async def cancel(self, ctx) -> None:
        try:
            name = str(ctx.message.author).split("#")[0]

            for d in self.duels:
                if d.challenger == ctx.message.author:
                    self.duels.remove(d)
                    await self.bot.send_message(ctx.message.channel, "{0} has cancelled their duel with {1.mention}".format(name, d.opponent))
                    return

            await self.bot.send_message(ctx.message.channel, "You have no duels to cancel")
        except Exception as e:
            await self.bot.handle_error(e, "cancel")

def setup(bot) -> None:
    bot.add_cog(BunkRPG(bot))