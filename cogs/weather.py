import sched, time, json
import urllib.request
from discord.ext import commands
from datetime import datetime
from .util.cog_wheel import CogWheel

HELP_DESCRIPTION = """
    Retrieve the forecast/weather for a given zip. Default=Baltimore
"""

WEATHER_API = "http://api.wunderground.com/api/"

class Weather(CogWheel):
    def __init__(self, bot, token):
        CogWheel.__init__(self, bot)
        self.token = token
        self.zip = "21201"
        #self.get_daily_weather()

    @property
    def weather_api(self):
        return WEATHER_API + self.token + "/conditions/q/" + self.zip + "/format.json"

    @property
    def forecast_api(self):
        return WEATHER_API + self.token + "/forecast10day/q/" + self.zip + "/format.json"

    @commands.command(pass_context=True, cls=None, help=HELP_DESCRIPTION)
    async def weather(self, ctx):
        try:
            await self.bot.send_typing(ctx.message.channel)

            params = "".join(self.get_cmd_params(ctx))
            if "zip" in params:
                self.zip = params.split("zip")[1].split("=")[1]
            else:
                self.zip = "21201"

            weather = json.loads(urllib.request.urlopen(self.weather_api).read())
            conditions = weather["current_observation"]
            wu = conditions["image"]["url"]
            thumb = conditions["icon_url"]

            location = conditions["display_location"]["full"]
            temp = str(conditions["temp_f"]) + " (F)" 
            feels = str(conditions["feelslike_f"]) + " (F)"

            condition_string = "Temperature: " + temp + "\nFeels like: " + feels

            if conditions["wind_mph"] > 0:
                condition_string += "\n\nCurrent winds " + conditions["wind_dir"] + " at " + str(conditions["wind_mph"]) + " mph"

            if conditions["precip_today_in"] != "0.00":
                condition_string += "\n\nPrecip accumulated today: " + conditions["precip_today_in"] + " inches "

            await self.send_message("Current conditions in " + location, condition_string, thumb, "Data provided by http://www.wunderground.com", wu)
        except:
            await self.send_message_plain("Bad command!")


    @commands.command(pass_context=True, cls=None, help=HELP_DESCRIPTION)
    async def forecast(self, ctx):
        await self.bot.send_typing(ctx.message.channel)

        params = "".join(self.get_cmd_params(ctx))
        if "zip" in params:
            self.zip = params.split("zip")[1].split("=")[1]
        else:
            self.zip = "21201"

        conditions = json.loads(urllib.request.urlopen(self.weather_api).read())
        obs = conditions["current_observation"]
        wu = obs["image"]["url"]
        location = obs["display_location"]["full"]
        
        weather = json.loads(urllib.request.urlopen(self.forecast_api).read())
        
        forecast_txt = weather["forecast"]["txt_forecast"]["forecastday"]
        forecast_simple = weather["forecast"]["simpleforecast"]["forecastday"]

        forecast_title = "3 Day forecast for " + location
        forecast_message = ""

        for day in range(0, 3, 1):
            fs = forecast_simple[day]
            ft = forecast_txt[day*2]
            ftt = forecast_txt[(day*2)+1]

            date = str(fs["date"]["month"]) + "/" + str(fs["date"]["day"])

            forecast_message += date + "\n"
            forecast_message += ft["title"] + " " + ft["fcttext"] + "\n"
            forecast_message += ftt["title"] + " " + ftt["fcttext"]
            forecast_message += "\n\n"

        await self.send_message(forecast_title, forecast_message, None, "Data provided by http://www.wunderground.com", wu) 


    async def get_daily_weather(self):
        print("hi")
        return


def setup(bot):
    with open("config.json", "r") as config:
        conf = json.load(config)
        bot.add_cog(Weather(bot, conf["weather"]))
        
