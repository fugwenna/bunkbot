"""
Zip-code driven weather forecast and current conditions
based on data retrieved from weather underground
"""
import uuid, asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup
from urllib import request
from discord import Embed
from discord.ext.commands import command
from src.bunkbot import BunkBot
from src.cogs.weather.weather_result import WeatherResult
from src.cogs.weather.radar_result import RadarResult
from src.storage.db import database
from src.util.constants import DB_WEATHER

WEATHER_DESCRIPTION = """Retrieve a current snapshot of todays weather based on zip code.\n
    param: zip - optionally pass a zip code. Default is Baltimore (21201).
        Example: !weather zip=90210
    \n
    param: --full (or -f) - display a 3 day forcast (day/night) for the provided zip code.\n
    Optionally provide a number (1-3) for 1, 2, or 3 day forecast
        Example: !weather zip=90210 2
"""

WEATHER_API = "http://api.wunderground.com/api/"
RADAR_QUERY = "http://www.intellicast.com/Search.axd?q="
RADAR_IMAGE = "http://www.intellicast.com/National/Radar/Current.aspx?location={0}&animate=true"

class Weather:
    def __init__(self, bot: BunkBot):
        self.bot = bot
        self.zip = "20201"
        self.token = database.get(DB_WEATHER)
        BunkBot.on_bot_initialized += self.wire_daily_forecast


    # dynamic property that will be used to
    # find the current weather conditions
    @property
    def weather_api(self) -> str:
        return WEATHER_API + self.token + "/conditions/q/" + self.zip + "/format.json"


    # dynamic property that will be used to
    # find a 3-day forecast
    @property
    def forecast_api(self)-> str:
        return WEATHER_API + self.token + "/forecast10day/q/" + self.zip + "/format.json"


    # start the daily forecast event loop
    # once the main bot has been initialized
    # 9AM UTC - 13
    async def wire_daily_forecast(self) -> None:
        try:
            scheduler = AsyncIOScheduler()
            scheduler.add_job(self.send_daily_forecast, trigger="cron", hour=14, misfire_grace_time=120)
            scheduler.start()

            if not scheduler.running:
                asyncio.get_event_loop().run_forever()
        except Exception as e:
            await self.bot.handle_error(e, "wire_daily_forecast")


    # daily forecast for the the
    # default Baltimore zip
    async def send_daily_forecast(self) -> None:
        try:
            self.zip = "21201"

            curr_weather_result = await self.bot.http_get(self.weather_api)
            forecast_result = await self.bot.http_get(self.forecast_api)

            if curr_weather_result is not None and forecast_result is not None:
                weather = WeatherResult(curr_weather_result, forecast_result, True, 1)

                embed = Embed(title=weather.title, description=weather.conditions, color=int("008cba", 16))
                embed.set_footer(text=weather.credit, icon_url=weather.wu_icon)
                embed.set_thumbnail(url=weather.thumb)

                await self.bot.say_to_channel(self.bot.general, None, embed)
        except Exception as e:
            await self.bot.handle_error(e, "send_daily_forecast")


    # executable command which will
    # display current weather conditions for
    # a given zip code
    @command(pass_context=True, cls=None, help=WEATHER_DESCRIPTION)
    async def weather(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)
            self.set_zip(ctx)

            curr_weather_result = await self.bot.http_get(self.weather_api)
            forecast_result = await self.bot.http_get(self.forecast_api)

            if curr_weather_result is not None and forecast_result is not None:
                weather = WeatherResult(curr_weather_result, forecast_result, self.as_full(ctx))

                embed = Embed(title=weather.title, description=weather.conditions, color=int("008cba", 16))
                embed.set_footer(text=weather.credit, icon_url=weather.wu_icon)
                embed.set_thumbnail(url=weather.thumb)

                await self.bot.say(embed=embed)
        except Exception as e:
            await self.bot.handle_error(e, "weather", ctx)


    # link local maryland radar from
    # the intellicast updated gif - cache bust with uuid
    @command(pass_context=True, cls=None, help="View Radar based on zip")
    async def radar(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)
            self.set_zip(ctx)

            radar_location = await self.bot.http_get("{0}{1}".format(RADAR_QUERY, self.zip))

            if radar_location is not None:
                radar_result = RadarResult(radar_location)

                if not radar_result.location_found:
                    await self.bot.say("Cannot locate radar for location '{0}'".format(self.zip))
                    return

                url = RADAR_IMAGE.format(radar_result.id)

                response = request.urlopen(url)
                html = response.read().decode()
                response.close()

                img = BeautifulSoup(html, "html.parser").find("img", id="map")["src"]

                await self.bot.say("{0}?{1}".format(img, uuid.uuid4()))
        except Exception as e:
            await self.bot.handle_error(e, "radar", ctx)


    # set the zip code
    # based on passed params
    def set_zip(self, ctx) -> None:
        params = self.bot.get_cmd_params(ctx)
        self.zip = "21201"

        if len(params) > 0:
            if "zip" in params[0]:
                self.zip = params[0].split("zip")[1].split("=")[1]
            elif params[0] is not "" and len(params[0]) == 5:
                self.zip = params[0]


    # print the full forecast weather
    def as_full(self, ctx) -> bool:
        params = self.bot.get_cmd_params(ctx)

        if len(params) == 0:
            return False
        elif len(params) == 1:
            return "--full" in params[0] or "-f" in params[0]
        elif len(params) == 2:
            return "--full" in params[1] or "-f" in params[1]


def setup(bot: BunkBot) -> None:
    bot.add_cog(Weather(bot))
