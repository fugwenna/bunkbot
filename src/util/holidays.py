"""
Cron task that will fire an event every day to
BunkBot when a holiday occurs - major holiday dates
will be celebrated with @everyone
"""
import pytz, asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from .event_hook import EventHook

now_year = datetime.now(tz=pytz.timezone("US/Eastern")).year

HOLIDAYS = [{
    "date": "01/01/{0}".format(now_year),
    "midnight": True,
    "message": "@everyone :champagne: :champagne: :champagne: :fireworks: :sparkler: HAPPY NEW YEAR!!!!1!!!11one1!!eleven!!111! :sparkler: :fireworks: :champagne: :champagne: :champagne:"
}, {
    "date": "10/31/{0}".format(now_year),
    "midnight": False,
    "message": "@everyone :jack_o_lantern: :jack_o_lantern: HAPPY HALLOWEEN!!!!!!!!!:jack_o_lantern: :jack_o_lantern: "
}]

#["1/1", "7/4", "10/31", "12/24", "12/25"]

class Holiday:
    on_holiday = EventHook()

    # at midnight every day, loop over the major
    # holidays and see which ones will be fired - off case new years
    # day where the event is fired at midnight - otherwise, fire the
    # event every day at a random interval of noon, 3PM, 6PM, and 8PM?
    @staticmethod
    async def send_midnight_greeting() -> None:
        global now_year

        now = datetime.now(tz=pytz.timezone("US/Eastern"))
        now_year = now.year
        formatted = "{0:%m/%d/%Y}".format(now)

        for holiday in HOLIDAYS:
            if holiday["midnight"] and holiday["date"] == formatted:
                await Holiday.on_holiday.fire(holiday["message"])


    # at midnight every day, loop over the major
    # holidays and see which ones will be fired - off case new years
    # day where the event is fired at midnight - otherwise, fire the
    # event every day at a random interval of noon, 3PM, 6PM, and 8PM?
    @staticmethod
    async def send_evening_greeting() -> None:
        global now_year

        now = datetime.now(tz=pytz.timezone("US/Eastern"))
        now_year = now.year
        formatted = "{0:%m/%d/%Y}".format(now)

        for holiday in HOLIDAYS:
            if not holiday["midnight"] and holiday["date"] == formatted:
                await Holiday.on_holiday.fire(holiday["message"])


    # start the static timer
    # when BunkBot initializes
    @staticmethod
    async def start_timer() -> None:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(Holiday.send_midnight_greeting, trigger="cron", hour=0)
        scheduler.add_job(Holiday.send_evening_greeting, trigger="cron", hour=18)
        scheduler.start()
        try:
            asyncio.get_event_loop().run_forever()
        except:
            pass



