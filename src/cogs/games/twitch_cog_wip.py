from urllib.request import HTTPError, URLError, socket
from twitch import TwitchClient
from src.bunkbot import BunkBot
from src.storage.db import database
from src.util.async import AsyncSchedulerHelper
from src.util.constants import DB_TWITCH_ID
from src.util.constants import CHANNEL_GAMING

TWITCH_URL: str = "https://api.twitch.tv/helix/streams"

"""
Class to handle a twitch stream check
every 60 minutes and allow people to add urls
"""
class TwitchCog:
    def __init__(self, bot: BunkBot):
        self.bot: BunkBot = bot
        #self.twitch_client = TwitchClient(client_id=database.get(DB_TWITCH_ID))
        #BunkBot.on_bot_initialized += self.wire_stream_listener


    async def get_streams(self) -> None:
        try:
            channel = self.twitch_client.streams.get_stream_by_user("blizzheroes")
            print(channel.name)

        except socket.timeout:
            await self.bot.handle_error("http timeout", "get_streams")
        except (HTTPError, URLError) as uhe:
            await self.bot.handle_error(uhe, "get_streams")
        except Exception as e:
            await self.bot.handle_error(e, "get_streams")


    # wire up the hourly even that will
    # search for twitch streams
    async def wire_stream_listener(self) -> None:
        try:
            AsyncSchedulerHelper.add_job(self.get_streams, trigger="interval", seconds=10)
        except Exception as e:
            await self.bot.handle_error(e, "wire_stream_listener")


def setup(bot: BunkBot) -> None:
    bot.add_cog(TwitchCog(bot))
