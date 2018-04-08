"""
Holiday greetings
"""
import datetime, asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Embed
from re import match
from tinydb import Query
from discord.ext.commands import command, Context
from src.bunkbot import BunkBot
from src.util.bunk_exception import BunkException
from src.util.bunk_user import BunkUser
from src.util.event_hook import EventHook
from src.util.helpers import EST
from src.storage.db import database

DESCRIPTION = """Add a holiday greeting for the server 

ex: !holiday 1/1 0 HAPPY NEW YEAR
ex: !holiday 7/4 12 HAPPY FOURTH OF JULY LOL 

"""
class HolidayCog:
    on_holiday = EventHook()

    def __init__(self, bot: BunkBot):
        self.bot = bot
        BunkBot.on_bot_initialized += self.wire_holiday_check


    # start the daily forecast event loop
    # once the main bot has been initialized
    # 9AM UTC - 13
    async def wire_holiday_check(self) -> None:
        try:
            hours = []
            holidays = database.holidays.all()
            scheduler = AsyncIOScheduler()

            for holiday in holidays:
                exists = [h for h in hours if h == holiday["hour"]]
                if len(exists) == 0:
                    hours.append(holiday["hour"])
                    scheduler.add_job(self.send_holiday_greeting, trigger="cron", hour=int(holiday["hour"]), misfire_grace_time=120, timezone=EST)
                    scheduler.start()

            if not scheduler.running:
                asyncio.get_event_loop().run_forever()
        except Exception as e:
            await self.bot.handle_error(e, "wire_holiday_check")


    #@command(pass_context=True, cls=None, help=DESCRIPTION)
    async def holiday(self, ctx: Context) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            cmds = self.bot.get_cmd_params(ctx)

            if len(cmds) < 3:
                await self.bot.say("A date, hour of day and message is required for a holiday (mm/dd format, ex: 1/1 or 03/21)")
                return

            date = cmds[0]

            try:
                datetime.datetime.strptime(date, "%m/%d")
            except ValueError:
                await self.bot.say("Invalid date format(mm/dd, ex: 1/1 or 03/21)")
                return

            hour = cmds[1]

            if not hour.isdigit():
                await self.bot.say("Hour of day must be a valid number 0-23")
                return

            message = " ".join(cmds[2:])
            database.holidays.insert({"date": date, "hour": hour, "message": message})
            await self.bot.say("Holiday added!")

        except Exception as e:
            await self.bot.handle_error(e, "holiday")


    #@command(pass_context=True, cls=None, help="Get a list of holidays")
    async def holidays(self, ctx: Context) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)
            holidays = database.holidays.all()

            dates = []
            hours = []
            messages = []

            for holiday in holidays:
                dates.append(holiday["date"])
                hours.append(holiday["hour"])
                messages.append(holiday["message"])

            embed = Embed(title="Holiday Greetings", color=int("19CF3A", 16))
            embed.add_field(name="Date", value="\n".join(dates), inline=True)
            embed.add_field(name="Hour", value="\n".join(hours), inline=True)
            embed.add_field(name="Message", value="\n".join(messages), inline=True)

            await self.bot.say(embed=embed)

        except Exception as e:
            await self.bot.handle_error(e, "holiday")


    async def send_holiday_greeting(self) -> None:
        holidays = database.holidays.all()

#def setup(bot) -> None:
#    bot.add_cog(HolidayCog(bot))