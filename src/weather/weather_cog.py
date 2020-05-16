from discord import Embed
from discord.ext.commands import command, Context, Cog

from .weather_constants import WEATHER_API_ICON_URL, WEATHER_API_MAP_URL
from .weather_result import WeatherResult
from .weather_service import WeatherService
from ..bunkbot import BunkBot
from ..core.registry import WEATHER_SERVICE


WEATHER_DESCRIPTION: str = """Get the current weather based on zipcode \n
    Example: !weather 21201
"""
class Weather(Cog):
    def __init__(self, weather: WeatherService):
        self.weather_svc: WeatherService = weather


    @command(help=WEATHER_DESCRIPTION)
    async def weather(self, ctx: Context) -> None:
        try:
            result: WeatherResult = await self.weather_svc.get_weather_by_zip(ctx)
            
            embed = Embed(
                title="Weather in {0} (F)".format(result.city), 
                description=result.weather["description"], 
                color=int("008cba", 16), 
                url=WEATHER_API_MAP_URL.format(result.coord_y, result.coord_x)
            )

            embed.add_field(name="Temperature", value=result.weather_temp, inline=False)
            embed.add_field(name="High", value=result.weather_max, inline=True)
            embed.add_field(name="Low", value=result.weather_min, inline=True)
            embed.add_field(name="Humidity", value=result.weather_humidity, inline=True)
            embed.set_thumbnail(url=WEATHER_API_ICON_URL.format(result.icon_url))

            await ctx.send(embed=embed)
        except Exception as e:
            await self.weather_svc.channel.log_error(e, "weather")


def setup(bot: BunkBot) -> None:
    bot.add_cog(Weather(WEATHER_SERVICE))
