from re import sub
from discord import Embed
from discord.ext.commands import command
from src.cogs.rpg.duel import Duel
from src.cogs.rpg.progress_bar import ProgressBar
from src.util.helpers import calc_req_xp
from src.storage.db import database
from src.util.bunk_user import BunkUser
from src.util.bunk_exception import BunkException
from src.bunkbot import BunkBot


"""
RPG commands  
"""
class BunkRPG:
    def __init__(self, bot: BunkBot):
        self.bot = bot
        self.duels = []
        BunkUser.on_level_up += self.ding


    # DING - user has leveled up
    # inform them and update their server permissions
    async def ding(self, member, value):
         if member.name != "fugwenna":
            await self.bot.say_to_channel(self.bot.general, ":bell: DING! {0.mention} has advanced to level {1}!".format(member, value))


    # get the top 10 leader board
    # sorting by level and xp
    @command(pass_context=True, cls=None, help="Get the current leader board", aliases=["leaders", "ranks", "levels", "leaderboard"])
    async def leader(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            players = sorted([u for u in self.bot.users if u.xp >= 0],
                             key=lambda x: (x.level, x.xp), reverse=True)[:9]

            names = []
            levels = []
            xps = []

            for p in players:
                names.append(sub(r"[^A-Za-z]+", "", p.name))
                levels.append(str(p.level))
                xps.append(str(p.xp))

            embed = Embed(title="", color=int("19CF3A", 16))
            embed.add_field(name="Name", value="\n".join(names), inline=True)
            embed.add_field(name="Level", value="\n".join(levels), inline=True)
            embed.add_field(name="Total XP", value="\n".join(xps), inline=True)

            await self.bot.say(embed=embed)
        except Exception as e:
            await self.bot.handle_error(e, "leaders")


    # allow users to print out their current level
    # or the level of another user, which will display
    # in n of 20 blocks based on pct to next level
    @command(pass_context=True, help="Print your current level", aliases=["ranks2"])
    async def level(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            user: BunkUser = self.bot.get_user(ctx.message.author.name)
            color = ctx.message.author.color

            params = self.bot.get_cmd_params(ctx)

            # user is getting the level of
            # another bunk user
            if len(params) > 0:
                param_user: BunkUser = self.bot.get_user(" ".join(params[0:]))
                user = param_user
                color = param_user.member.color

            progress_bar = ProgressBar(user)
            embed = Embed(title="{0}: Level {1}".format(user.name, user.level), description=progress_bar.draw(), color=color)

            if len(params) > 0:
                embed.set_footer(text="{0} is currently {1}% to level {2}".format(user.name, progress_bar.pct, user.next_level))
            else:
                embed.set_footer(text="You are currently {0}% to level {1}".format(progress_bar.pct, user.next_level))

            await self.bot.say(embed=embed)

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "level")


    # challenge another user to a duel
    # if they are currently, dueling throw an error
    # a user cannot challenge themselves to a duel
    @command(pass_context=True, help="Challenge another user to a duel", aliases=["challenge2"])
    async def duel(self, ctx) -> None:
        try:
            challenger: BunkUser = self.bot.get_user(ctx.message.author.name)
            param = self.bot.get_cmd_params(ctx)

            if len(param) == 0:
                await self.bot.say("You must supply a challenger!")
                return

            opponent: BunkUser = self.bot.get_user(" ".join(param[0:]))
            challenger.duel = Duel(challenger, opponent)
            self.duels.append(challenger.duel)

            msg = """:triangular_flag_on_post: {0.mention} is challenging {1.mention} to a duel! 
            Type !accept to duel, or !reject to run away like a little biiiiiiiiiiiiitch""".format(challenger, opponent)

            await self.bot.say(msg)

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "duel")


    # accept a duel from another BunkUser
    # and lock the duel for both users
    @command(pass_context=True, help="Challenge another user to a duel")
    async def accept(self, ctx) -> None:
        try:
            bunk_user = self.bot.get_user(ctx.message.author.name)
            duels = [d for d in self.duels if d.opponent.name == bunk_user.name]

            if len(duels) == 0:
                await self.bot.say("You have no duels to accept")
                return

            duel: Duel = duels[0]
            await duel.execute()
            self.duels.remove(duel)

            embed = Embed(title=":crossed_swords: {0} vs {1}".format(duel.challenger.name, duel.opponent.name),
                          color=int("FF0000", 16))
            embed.add_field(name="Name", value="\n".join([duel.challenger.name, duel.opponent.name]), inline=True)
            embed.add_field(name="Damage",
                            value="\n".join([str(duel.challenger.duel_roll), str(duel.opponent.duel_roll)]),
                            inline=True)

            await self.bot.say(embed=embed)

            # todo - calculate within duel class
            xp_lost = 5.0
            if duel.loser.xp > 5.0:
                await self.bot.say("{0.mention} wins 5 xp from {1}!".format(duel.winner, duel.loser.name))
            elif 5.0 > duel.loser.xp > 0.0:
                xp_lost = duel.loser.xp
                await self.bot.say("{0.mention} wins {1}'s remaining xp!".format(duel.winner, duel.loser.name))
            elif duel.loser.xp == 0:
                await self.bot.say("{0.mention} wins, but {1} has no xp to give!".format(duel.winner, duel.loser.name))

            if duel.loser.xp > 0: database.update_user_xp(duel.loser.member, -xp_lost)
            loser_level_xp = calc_req_xp(duel.loser.level)

            if duel.loser.level > 1 and duel.loser.xp - xp_lost < loser_level_xp:
                duel.loser.from_database(database.update_user_level(duel.loser.member, -1))
                await self.bot.say("{0.mention} has lost a level!".format(duel.loser))

            if xp_lost > 0:
                await duel.winner.update_xp(xp_lost, True)

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "accept")


    # reject a duel from another BunkUser
    # and remove the lock for both users
    @command(pass_context=True, cls=None, help="Reject a duel")
    async def reject(self, ctx) -> None:
        try:
            found = False
            user: BunkUser = self.bot.get_user(ctx.message.author.name)

            for d in self.duels:
                if d.opponent.name == user.name:
                    found = True
                    d.challenger.duel = None
                    d.opponent.duel = None
                    self.duels.remove(d)
                    await self.bot.say(":exclamation: {0.mention} has rejected a duel with {1.mention}".format(d.opponent, d.challenger))

            if not found:
                await self.bot.say("You have no duels to reject")

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "cancel")


    # cancel a duel from another BunkUser
    # and remove the lock for both users
    @command(pass_context=True, cls=None, help="Cancel a duel")
    async def cancel(self, ctx) -> None:
        try:
            found = False
            user: BunkUser = self.bot.get_user(ctx.message.author.name)

            for d in self.duels:
                if d.challenger.name == user.name:
                    found = True
                    d.challenger.duel = None
                    d.opponent.duel = None
                    self.duels.remove(d)
                    await self.bot.say("{0.mention} has cancelled their duel with {1.mention}".format(d.challenger, d.opponent))

            if not found:
                await self.bot.say("You have no duels to cancel")

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "cancel")


def setup(bot: BunkBot) -> None:
    #return
    bot.add_cog(BunkRPG(bot))