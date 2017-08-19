"""
Zip-code driven weather forecast and current conditions
based on data retrieved from weather underground
"""
import uuid, re
from bs4 import BeautifulSoup
from urllib import request, parse
from discord import Embed
from discord.ext import commands
from src.bunkbot import BunkBot
from src.cogs.weather.weather_result import WeatherResult
from src.storage.db import database

WEATHER_DESCRIPTION = """Retrieve a current snapshot of todays weather based on zip code.\n
    param: zip - optionally pass a zip code. Default is Baltimore (21201).
        Example: !weather zip=90210
    \n
    param: --full (or -f) - display a 3 day forcast (day/night) for the provided zip code.
"""

WEATHER_API = "http://api.wunderground.com/api/"
RADAR_QUERY = "http://www.intellicast.com/Search.axd?q="

class Weather:
    def __init__(self, bot: BunkBot):
        self.bot = bot
        self.zip = "20201"
        self.token = database.get("weather")


    # dynamic property that will be used to
    # find the current weather conditions
    @property
    def weather_api(self):
        return WEATHER_API + self.token + "/conditions/q/" + self.zip + "/format.json"


    # dynamic property that will be used to
    # find a 3-day forecast
    @property
    def forecast_api(self):
        return WEATHER_API + self.token + "/forecast10day/q/" + self.zip + "/format.json"


    # executable command which will
    # display current weather conditions for
    # a given zip code
    @commands.command(pass_context=True, cls=None, help=WEATHER_DESCRIPTION)
    async def weather(self, ctx):
        try:
            await self.bot.send_typing(ctx.message.channel)
            self.set_zip(ctx)

            curr_weather_result = self.bot.http_get(self.weather_api)
            forecast_result = self.bot.http_get(self.forecast_api)

            weather = WeatherResult(curr_weather_result, forecast_result, self.as_full(ctx))

            embed = Embed(title=weather.title, description=weather.conditions, color=int("008cba", 16))
            embed.set_footer(text=weather.credit, icon_url=weather.wu_icon)
            embed.set_thumbnail(url=weather.thumb)

            await self.bot.say(embed=embed)
        except Exception as e:
            await self.bot.handle_error(e, "weather")


    # link local maryland radar from
    # the intellicast updated gif - cache bust with uuid
    @commands.command(pass_context=True, cls=None, help="View Radar based on zip")
    async def radar(self, ctx):
        try:
            await self.bot.send_typing(ctx.message.channel)
            self.set_zip(ctx)

            # todo - radar result
            us_locs = self.bot.http_get("{0}{1}".format(RADAR_QUERY, self.zip))["results"]["locations"]["location"]
            if len(us_locs) == 0:
                await self.bot.say("Cannot locate radar for location '{0}'".format(self.zip))
                return

            loc = us_locs[0]["id"]
            url = "http://www.intellicast.com/National/Radar/Current.aspx?location={0}&animate=true".format(loc)

            response = request.urlopen(url)
            html = response.read().decode()
            response.close()

            img = BeautifulSoup(html, "html.parser").find("img", id="map")["src"]

            await self.bot.say("{0}?{1}".format(img, uuid.uuid4()))
        except Exception as e:
            await self.bot.handle_error(e, "radar")


    # set the zip code
    # based on passed params
    def set_zip(self, ctx):
        params = "".join(self.bot.get_cmd_params(ctx))

        if "zip" in params:
            self.zip = params.split("zip")[1].split("=")[1]
        elif int(params):
            self.zip = params
        else:
            self.zip = "21201"


    # print the full forecast weather
    def as_full(self, ctx):
        params = "".join(self.bot.get_cmd_params(ctx))
        return "--full" in params or "-f" in params


def setup(bot: BunkBot) -> None:
    bot.add_cog(Weather(bot))