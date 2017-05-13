import json, uuid
from discord.ext import commands
from datetime import datetime
from threading import Timer
from .util.cog_wheel import CogWheel
from .util.weather_wrapper import WeatherWrapper

WEATHER_DESCRIPTION = """Retrieve a current snapshot of todays weather based on zip code.\n
    param: zip - optionally pass a zip code. Default is Baltimore (21201).
        Example: !weather zip=90210
    \n
    param: --full (or -f) - display a 3 day forcast (day/night) for the provided zip code.
"""

WEATHER_API = "http://api.wunderground.com/api/"

class Weather(CogWheel):
    def __init__(self, bot, token):
        CogWheel.__init__(self, bot)
        self.token = token
        self.zip = "21201"
        self.daily_set = False
        self.timer = None
        #human_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=time.seconds)

    """
    Dynamic property that will be used to
    find the current weather conditions
    """
    @property
    def weather_api(self):
        return WEATHER_API + self.token + "/conditions/q/" + self.zip + "/format.json"

    """
    Dynamic property that will be used to
    find a 3-day forecast
    """
    @property
    def forecast_api(self):
        return WEATHER_API + self.token + "/forecast10day/q/" + self.zip + "/format.json"

    """
    Dynamic property that will be used
    to find any alerts
    """
    @property
    def alert_api(self):
        return WEATHER_API + self.token + "/alerts/q/" + self.zip + "/format.json"

    """
    Executable command which will
    display current weather conditions for
    a given zip code
    """
    @commands.command(pass_context=True, cls=None, help=WEATHER_DESCRIPTION)
    async def weather(self, ctx):
        try:
            await self.bot.send_typing(ctx.message.channel)
            self.set_zip(ctx)

            curr_weather_result = self.http_get(self.weather_api)
            forecast_result = self.http_get(self.forecast_api)
            #alert_result = self.http_get(self.alert_api)

            weather = WeatherWrapper(curr_weather_result, forecast_result, [], self.as_full(ctx))
            
            await self.send_message(weather.title, weather.conditions, weather.thumb, weather.credit, weather.wu_icon)
            await self.get_daily_weather()
        except Exception as e:
            print(e)
            await self.handle_error(e)

    """
    Link baltimore radar
    """
    @commands.command(pass_context=True, cls=None, help="View Maryland Radar")
    async def radar(self, ctx):
        rad = "http://images.intellicast.com/WxImages/RadarLoop/shd_None_anim.gif?{}".format(uuid.uuid4())
        try:
            await self.bot.send_typing(ctx.message.channel)
            await self.send_message_plain(rad)
        except Exception as e:
            await self.handle_error(e)

    """
    Display the current weather 3 times a day,
    with a forecast twice a day
    """
    async def get_daily_weather(self):
        if not self.daily_set:
            self.daily_set = True
            x = datetime.today()
            y = x.replace(day=x.day, hour=7, minute=0, second=0, microsecond=0)
            delta_t=y-x
            secs = delta_t.seconds+1
            t = Timer(secs, self.say_daily_weather)
            t.start()

    """
    Print the daily weather
    """
    async def say_daily_weather(self):
        self.set_zip(ctx)
        
        curr_weather_result = self.http_get(self.weather_api)
        forecast_result = self.http_get(self.forecast_api)

        weather = WeatherWrapper(curr_weather_result, forecast_result, True)
            
        await self.send_message(weather.title, weather.conditions, weather.thumb, weather.credit, weather.wu_icon)

    """
    Set the zip code based on passed params
    """
    def set_zip(self, ctx):
        params = "".join(self.get_cmd_params(ctx))
        if "zip" in params:
            self.zip = params.split("zip")[1].split("=")[1]
        else:
            self.zip = "21201"

    """
    Print the full forecast weather
    """
    def as_full(self, ctx):
        params = "".join(self.get_cmd_params(ctx))
        return "--full" in params or "-f" in params


def setup(bot):
    with open("config.json", "r") as config:
        conf = json.load(config)
        bot.add_cog(Weather(bot, conf["weather"]))
        
