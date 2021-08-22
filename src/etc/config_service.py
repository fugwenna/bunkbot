import json
from os import path

from ..core.bunk_exception import BunkException
from .config_constants import \
    DEFAULT_CONFIG_PATH, KEY_YOUTUBE, TOKEN_DISCORD, \
    CHANNEL_PRIMARY, CHANNEL_LOGS, CHANNEL_CUSTOM_GAMES, CHANNEL_XKCD, \
    KEY_WEATHER, KEY_CLEVERBOT, KEY_TENOR


"""
Unlike database service which is used to store things like game names, user stats,
streams, etc., this service is responsible for reading from config.json, 
which is specifically for known/expected constants, api keys, and other things
"""
class ConfigService:
    def __init__(self):
        self.raise_error_on_bad_config: bool = True

    
    @property
    def discord_token(self) -> str:
        return self._get(TOKEN_DISCORD)


    @property
    def primary_channel(self) -> str:
        return self._get(CHANNEL_PRIMARY)


    @property
    def log_channel(self) -> str:
        return self._get(CHANNEL_LOGS)

    
    @property
    def custom_games_channel(self) -> str:
        return self._get(CHANNEL_CUSTOM_GAMES)


    @property
    def xkcd_channel(self) -> str:
        return self._get(CHANNEL_XKCD)


    @property
    def cleverbot_api_key(self) -> str:
        return self._get(KEY_CLEVERBOT)


    @property
    def weather_api_key(self) -> str:
        return self._get(KEY_WEATHER)


    @property
    def tenor_api_key(self) -> str:
        return self._get(KEY_TENOR)


    @property
    def youtube_api_key(self) -> str:
        return self._get(KEY_YOUTUBE)


    def _get(self, name: str) -> str:
        if not path.exists(path.realpath(DEFAULT_CONFIG_PATH)):
            return None

        with open(DEFAULT_CONFIG_PATH, "r") as f:
            try:
                config = json.load(f)
                val: str = config[name]

                if self.raise_error_on_bad_config and (val is None or val.strip() == ""):
                    raise Exception()
                else:
                    return val
            except:
                if self.raise_error_on_bad_config:
                    raise BunkException("Error reading key '{0}' from config!".format(name))
                else:
                    return None
