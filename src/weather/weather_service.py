from discord.ext.commands import Context

from .weather_constants import WEATHER_API_BY_ZIP_URL
from .weather_result import WeatherResult
from ..bunkbot import BunkBot
from ..core.functions import get_cmd_params
from ..core.http import http_get
from ..core.service import Service
from ..channel.channel_service import ChannelService
from ..db.database_service import DatabaseService
from ..etc.config_service import ConfigService


"""
Core service to handle daily weather forecasts and
retrieval from the weather API
"""
class WeatherService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService, channel: ChannelService):
        super().__init__(bot, database)
        self.channel: ChannelService = channel

    
    # Get the weather for a given zip code (default baltimore)
    async def get_weather_by_zip(self, ctx: Context) -> WeatherResult:
        api_key: str = self.config.weather_api_key

        if api_key:
            zipcode: str = "21201"
            params: list = get_cmd_params(ctx)

            if len(params) > 0:
                p_zip: str = params[0]
                if p_zip.isdigit() and len(p_zip) == 5:
                    zipcode = p_zip

            result = await http_get(WEATHER_API_BY_ZIP_URL.format(zipcode, api_key))
        
            return WeatherResult(result)
