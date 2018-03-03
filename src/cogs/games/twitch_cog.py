import asyncio
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from urllib.request import HTTPError, URLError, socket
from src.bunkbot import BunkBot
from src.storage.db import database
from src.util.constants import DB_TWITCH_ID
from src.util.constants import CHANNEL_GAMING

TWITCH_URL: str = "https://api.twitch.tv/helix/streams"

"""
Class to handle a twitch stream check
every 30 minutes and allow people to add urls
"""
class TwitchCog:
    def __init__(self, bot: BunkBot):
        self.bot: BunkBot = bot
        BunkBot.on_bot_initialized += self.wire_stream_listener


    async def get_streams(self) -> None:
        try:
            headers = {"Client-ID": database.get(DB_TWITCH_ID)}
            req = requests.get(TWITCH_URL, headers=headers)

            print(req.text)
            #await self.bot.debug("\n".join(req.json()))

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
            scheduler = AsyncIOScheduler()
            scheduler.add_job(self.get_streams, trigger="interval", seconds=5, misfire_grace_time=120)
            scheduler.start()

            if not scheduler.running:
                asyncio.get_event_loop().run_forever()
        except Exception as e:
            await self.bot.handle_error(e, "wire_stream_listener")


def setup(bot: BunkBot) -> None:
    bot.add_cog(TwitchCog(bot))
