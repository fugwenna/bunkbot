"""
Cron task that will fire an event every day to
BunkBot when a holiday occurs - major holiday dates
will be celebrated with @everyone
"""
import pytz, asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from .event_hook import EventHook
from .helpers import EST

now_year = datetime.now(tz=pytz.timezone("US/Eastern")).year

HOLIDAYS = [{
    "date": "01/01/{0}".format(now_year),
    "midnight": True,
    "message": "@everyone :champagne: :champagne: :champagne: :fireworks: :sparkler: HAPPY NEW YEAR!!!!1!!!11one1!!eleven!!111! :sparkler: :fireworks: :champagne: :champagne: :champagne:"
}, {
    "date": "03/17/{0}".format(now_year),
    "midnight": False,
    "message": "@everyone :four_leaf_clover: :beers: :beer:  HAPPY ST PATTYS DAY OR WHATEVER YEEUHHH  :beer: :beers: :four_leaf_clover:"
}, {
    "date": "12/25/{0}".format(now_year),
    "midnight": False,
    "message": ":christmas_tree: :snowflake: :snowman2: Merry Christmas!!!! :snowman2: :snowflake: :christmas_tree:"
}, {
    "date": "10/31/{0}".format(now_year),
    "midnight": False,
    "message": "@everyone :jack_o_lantern: :jack_o_lantern: HAPPY HALLOWEEN!!!!!!!!!:jack_o_lantern: :jack_o_lantern:"
}, {
    "date": "11/23/{0}".format(now_year),
    "midnight": False,
    "message": "@everyone :turkey: :poultry_leg: :sweet_potato: HAPPY THANKSGIVING!!!!!!111!!! :sweet_potato: :poultry_leg: :turkey:"
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

        now = datetime.now(tz=EST)
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

        now = datetime.now(tz=EST)
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
        scheduler.add_job(Holiday.send_midnight_greeting, trigger="cron", hour=12, misfire_grace_time=60, timezone=EST)
        scheduler.add_job(Holiday.send_evening_greeting, trigger="cron", hour=8, misfire_grace_time=60, timezone=EST)
        scheduler.start()
        try:
            asyncio.get_event_loop().run_forever()
        except:
            pass



