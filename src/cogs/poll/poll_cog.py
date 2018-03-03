from discord import Embed
from discord.ext.commands import command, Context
from src.bunkbot import BunkBot
from src.util.bunk_exception import BunkException
from src.util.bunk_user import BunkUser
from .poll import Poll
from .option import Option
from .vote import Vote
from .result_bar import PollResultBar


class PollCog:
    def __init__(self, bot: BunkBot):
        self.bot = bot
        self.poll: Poll = Poll()

    @command(pass_context=True, cls=None, help="Create a poll", aliases=["mkpoll", "poll", "mp"])
    async def makepoll(self, ctx: Context) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            if self.poll.is_active:
                raise BunkException("{0} - Another poll is currently active by {1}"
                                    .format(ctx.message.author.mention, self.poll.author.mention))

            cmd = self.bot.get_cmd_params(ctx)
            if len(cmd) == 0:
                raise BunkException("Provide a question for the poll")

            question = " ".join(cmd)
            self.poll.is_active = True
            self.poll.author = self.bot.get_user_by_id(ctx.message.author.id)
            self.poll.question = question

            await self.bot.say("Created poll '{0}'".format(question))
            await self.bot.say("Type !option to add options (i.e. !option Vote for this!)")

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "makepoll")


    @command(pass_context=True, cls=None, help="Create an option", aliases=["option", "mkoption", "op", "mkop"])
    async def optionpoll(self, ctx: Context) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            if not self.poll.is_active:
                raise BunkException("{0} - There is no currently active poll which to add an option"
                                    .format(ctx.message.author.mention))

            cmd = self.bot.get_cmd_params(ctx)
            if len(cmd) == 0:
                raise BunkException("Please provide an option (i.e. !option dogs)")

            option = " ".join(cmd)

            self.poll.options.append(Option(option))
            await self.bot.say("Option '{0}' added".format(option))

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "optionpoll")


    @command(pass_context=True, cls=None, help="Remove an option at a given index", aliases=["rmoption", "or", "rmop"])
    async def optionremove(self, ctx: Context) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            if not self.poll.is_active:
                raise BunkException("{0} - There is no currently active poll which to add an option"
                                    .format(ctx.message.author.mention))

            cmd = self.bot.get_cmd_params(ctx)
            if len(cmd) == 0:
                raise BunkException("Please provide an option number to remove (type !options for list)")

            index = cmd[0]
            new_options = []

            opt = None
            for i in range(0, len(self.poll.options)):
                if i+1 != int(index):
                    new_options.append(self.poll.options[i])
                else:
                    opt = self.poll.options[i]

            self.poll.options = new_options
            await self.bot.say("Option '{0}' removed".format(opt.value))

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "optionremove")


    @command(pass_context=True, cls=None, help="Remove an option at a given index", aliases=["options", "og", "getops"])
    async def optionsget(self, ctx: Context) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            if not self.poll.is_active:
                raise BunkException("{0} - There is no currently active poll".format(ctx.message.author.mention))

            opt_list = []
            for i in range(0, len(self.poll.options)):
                opt_list.append("{0}. {1}".format(i+1, self.poll.options[i].value))

            embed = Embed(title="Poll: {0}".format(self.poll.question), description="\n".join(opt_list))
            await self.bot.say(embed=embed)

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "optionget")


    @command(pass_context=True, cls=None, help="Cancel a poll", aliases=["cpoll", "cp"])
    async def cancelpoll(self, ctx: Context) -> None:
        try:
            if not self.poll.is_active:
                raise BunkException("{0} - There is no currently active poll to cancel"
                                    .format(ctx.message.author.mention))

            bunk_user = self.bot.get_user_by_id(ctx.message.author.id)
            if bunk_user.name == self.poll.author.name:
                await self.bot.say("{0} poll cancelled".format(self.poll.author.mention))
                self.poll = Poll()

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "cancelpoll")


    @command(pass_context=True, cls=None, help="Run a poll", aliases=["vote", "vp"])
    async def votepoll(self, ctx: Context) -> None:
        try:
            if not self.poll.is_live:
                raise BunkException("{0} - There is no currently live poll for which to vote"
                                    .format(ctx.message.author.mention))

            cmd = self.bot.get_cmd_params(ctx)
            if len(cmd) == 0:
                raise BunkException("Please provide a number from the !options list")

            vote = int(cmd[0])

            if vote > len(self.poll.options) or vote < 1:
                raise BunkException("Not a valid vote")

            bunk_user: BunkUser = self.bot.get_user_by_id(ctx.message.author.id)
            voted = [x for x in self.poll.votes if x.user.name == bunk_user.name]

            option: Option = self.poll.options[vote-1]

            if len(voted) > 0:
                exists: Vote = voted[0]
                if exists.value == option.value:
                    raise BunkException("You can't vote for the same option more than once")
                else:
                    exists.value = option.value
            else:
                self.poll.votes.append(Vote(option.value, bunk_user))

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "votepoll")


    @command(pass_context=True, cls=None, help="Run a poll", aliases=["run", "rp"])
    async def runpoll(self, ctx: Context) -> None:
        try:
            if not self.poll.is_active:
                raise BunkException("{0} - There is no currently active poll to run".format(ctx.message.author.mention))

            if len(self.poll.options) == 0:
                raise BunkException("{0} - Poll has no options".format(ctx.message.author.mention))

            self.poll.is_active = False
            self.poll.is_live = True

            opt_list = []
            for i in range(0, len(self.poll.options)):
                opt_list.append("{0}. {1}".format(i + 1, self.poll.options[i].value))

            embed = Embed(title="Poll: {0}".format(self.poll.question), description="\n".join(opt_list), color=int("0CF03A", 16))
            await self.bot.say("@here Poll '{0}' is active! Type !vote <number> to select your choice (i.e. !vote 1)"
                               .format(self.poll.question))

            await self.bot.say(embed=embed)

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "runpoll")


    @command(pass_context=True, cls=None, help="Get the results of the poll", aliases=["results", "pollresults"])
    async def resultspoll(self, ctx: Context) -> None:
        try:
            bunk_user = self.bot.get_user_by_id(ctx.message.author.id)
            if bunk_user.name == self.poll.author.name:
                await self.bot.send_typing(ctx.message.channel)

                self.poll.is_active = False
                self.poll.is_live = False

                results = []
                winners = []
                current_best = 0

                for option in self.poll.options:
                    result = len([v for v in self.poll.votes if v.value == option.value])
                    bar = PollResultBar(result, len(self.poll.votes))
                    option.result = "{0}: {1} ({2} votes)".format(option.value, bar.draw(), result)
                    results.append(option)

                    if len(winners) == 0 or result == current_best:
                        winners.append(option)
                        current_best = result
                    elif result > current_best:
                        winners = [option]
                        current_best = result

                winner = ""

                if len(winners) > 1:
                    winner = "The result in a tie of {0} votes for:\n{1}".format(str(current_best), "\n".join([x.value for x in winners]))
                else:
                    winner = "The winner is '{0}' with {1} votes!".format(winners[0].value, str(current_best))

                bars ="\n".join([x.result for x in results])
                bars +="\n\n{0}".format(winner)

                title = "Poll '{0}' results:".format(self.poll.question)
                embed = Embed(title=title, description=bars, color=int("008cba", 16))

                await self.bot.say("@here The results for poll: '{0}' are in!".format(self.poll.question))
                await self.bot.say(embed=embed)
                self.poll = Poll()

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "resultspoll")


def setup(bot) -> None:
    bot.add_cog(PollCog(bot))