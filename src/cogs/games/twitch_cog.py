import datetime
from re import sub
from urllib.request import HTTPError, URLError, socket
from twitch import TwitchClient
from discord import Embed
from discord.ext import commands
from discord.ext.commands import command
from tinydb import Query
from src.bunkbot import BunkBot
from src.storage.db import database
from src.util.async import AsyncSchedulerHelper
from src.util.helpers import EST
from src.util.bunk_exception import BunkException
from src.util.constants import CHANNEL_GENERAL, ROLE_ADMIN, DB_TWITCH_ID, URL_REGEX

TWITCH_URL: str = "https://api.twitch.tv/helix/streams"
TWITCH_ICON: str = "https://vignette.wikia.nocookie.net/fallout/images/4/43/Twitch_icon.png/revision/latest?cb=20180507131302"

"""
Class to handle a twitch stream check
every 60 minutes and allow people to add urls
"""
class TwitchCog:
    def __init__(self, bot: BunkBot):
        self.bot: BunkBot = bot
        self.current_stream_ids = []
        self.twitch_client = TwitchClient(client_id=database.get(DB_TWITCH_ID))
        BunkBot.on_bot_initialized += self.wire_stream_listener


    # wire up the hourly even that will
    # search for twitch streams
    async def wire_stream_listener(self) -> None:
        try:
            AsyncSchedulerHelper.add_job(self.get_streams, trigger="interval", hours=1)
        except Exception as e:
            await self.bot.handle_error(e, "wire_stream_listener")


    # loop over saved streams in the database
    # and check whether they are streaming
    async def get_streams(self) -> None:
        try:
            now = datetime.datetime.now(EST)
            if 23 >= now.hour >= 10:
                streams = []
                for s in database.streams.all():
                    streams.append(s["name"])

                stream_ids = self.twitch_client.users.translate_usernames_to_ids(streams)

                for stream in stream_ids:
                    strm = self.twitch_client.streams.get_stream_by_user(stream.id)

                    if strm is not None:
                        if stream.id not in self.current_stream_ids:
                            self.current_stream_ids.append(stream.id)
                            ch = strm.channel

                            embed = Embed(title=ch.display_name, description=ch.status + "\n" + ch.url, color=int("392e5c", 16))
                            embed.set_footer(text="Currently playing {0}".format(strm.game), icon_url=TWITCH_ICON)
                            embed.set_thumbnail(url=ch.logo)

                            await self.bot.say_to_channel(self.bot.bot_logs, None, embed)
                    else:
                        if stream.id in self.current_stream_ids:
                            self.current_stream_ids.remove(stream.id)
                            await self.bot.say_to_channel(self.bot.bot_logs, "{0} is no longer streaming".format(stream.display_name))
            else:
                self.current_stream_ids = []

        except socket.timeout:
            await self.bot.handle_error("http timeout", "get_streams")
        except (HTTPError, URLError) as uhe:
            await self.bot.handle_error(uhe, "get_streams")
        except Exception as e:
            await self.bot.handle_error(e, "get_streams")


    # executable command which will
    # display current weather conditions for
    # a given zip code
    @commands.has_any_role(ROLE_ADMIN)
    @command(pass_context=True, cls=None, help="Add a stream to the database")
    async def stream(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx)

            params = self.bot.get_cmd_params(ctx)
            if len(params) == 0:
                raise BunkException("Enter a stream name")

            paramSplit = params[0].split("/")
            sname = paramSplit[len(paramSplit)-1]
            stream = database.streams.get(Query().name == sname)

            if stream is not None:
                raise BunkException("Stream '{0}' has already been added to the database {0}".format(sname))

            stream_ids = self.twitch_client.users.translate_usernames_to_ids([sname])
            if len(stream_ids) == 0:
                raise BunkException("Cannot find stream '{0}'".format(sname))

            database.streams.insert({"name": sname, "added_by": ctx.message.author.name})
            strm = self.twitch_client.streams.get_stream_by_user(stream_ids[0].id)

            if strm is None:
                await self.bot.say("Stream '{0}' has been added to the database, but is not currently streaming."
                                   .format(sname))
            else:
                await self.bot.say("Stream '{0}' has been added to the database and is now streaming: {1}"
                                   .format(sname, strm.channel.url))

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "stream")


    # list currently followed streams
    @commands.has_any_role(ROLE_ADMIN)
    @command(pass_context=True, cls=None, help="List currently followed streams")
    async def streams(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx)

            stream_names = []
            added_bys = []

            for s in database.streams.all():
                stream_names.append(s["name"])
                added_bys.append(s["added_by"])

            embed = Embed(title="Currently Followed Streams", color=int("19CF3A", 16))
            embed.add_field(name="Stream", value="\n".join(stream_names), inline=True)
            embed.add_field(name="Added By", value="\n".join(added_bys), inline=True)
            embed.set_thumbnail(url=TWITCH_ICON)

            await self.bot.say(embed=embed)

        except Exception as e:
            await self.bot.handle_error(e, "streams")

def setup(bot: BunkBot) -> None:
    bot.add_cog(TwitchCog(bot))
