import json
from os import path

from .config_constants import \
    DEFAULT_CONFIG_PATH, CHANNEL_PRIMARY, CHANNEL_LOGS


"""
Unlike database service which is used to store things like game names, user stats,
streams, etc., this service is responsible for reading from config.json, 
which is specifically for known/expected constants, api keys, and other things
"""
class ConfigService:
    @property
    def primary_channel(self) -> str:
        return self._get(CHANNEL_PRIMARY)


    @property
    def log_channel(self) -> str:
        return self._get(CHANNEL_LOGS)


    def _get(self, name: str) -> str:
        if not path.exists(path.realpath(DEFAULT_CONFIG_PATH)):
            return None

        with open(DEFAULT_CONFIG_PATH, "r") as f:
            try:
                config = json.load(f)
                return config[name]
            except:
                return None
