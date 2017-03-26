import sched, time, json
import urllib.request
from discord.ext import commands
from datetime import datetime
from .util.cog_wheel import CogWheel

HELP_DESCRIPTION = """
    Retrieve the weather for a given zip. Default=Baltimore
"""

WEATHER_API = "http://api.wunderground.com/api/"

class Weather(CogWheel):
    def __init__(self, bot, token):
        CogWheel.__init__(self, bot)
        self.zip = "21201"
        self.weather_api = WEATHER_API + token + "/conditions/q/" + self.zip + "/format.json"
        self.forecast_api = WEATHER_API + token + "/forcast/q/" + self.zip + "/format.json"

    @commands.command(pass_context=True, cls=None, help=HELP_DESCRIPTION)
    async def weather(self, ctx):
        await self.bot.send_typing(ctx.message.channel)
        zipcode = self.zip

        #todo
        #params = self.get_cmd_params(ctx)

        weather = json.loads(urllib.request.urlopen(self.weather_api).read())
        conditions = weather["current_observation"]
        wu = conditions["image"]["url"]
        thumb = conditions["icon_url"]

        location = conditions["display_location"]["full"]
        temp = str(conditions["temp_f"]) + " (F)" 
        feels = str(conditions["feelslike_f"]) + " (F)"
        
        await self.send_message("Current conditions in " + location, "Temperature: " + temp + "\nFeels like: " + feels, thumb, "Data provided by http://www.wunderground.com", wu)

    #@commands.command(pass_context=True, cls=None, help=HELP_DESCRIPTION)
    #async def forecast(self, ctx):
    #    await self.bot.send_typing(ctx.message.channel)
    #    forecast = json.loads(urllib.request.urlopen(self.forecast_api).read())
    #    await self.send_message_plain(forecast)


    async def get_daily_weather(self):
        return

def setup(bot):
    with open("config.json", "r") as config:
        conf = json.load(config)
        bot.add_cog(Weather(bot, conf["weather"]))
        
