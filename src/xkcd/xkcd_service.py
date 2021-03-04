from typing import List
from random import randint
from discord.ext.commands import Context
from discord import TextChannel, Embed

from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.daemon import DaemonHelper
from ..core.http import http_get
from ..core.functions import get_cmd_params
from ..core.service import Service
from ..db.database_service import DatabaseService
from ..etc.config_service import ConfigService


XKCD_BASE_URL: str = "https://xkcd.com"
XKCD_INFO_URL: str = "https://xkcd.com/info.0.json"
XKCD_JSON_URL: str = "https://xkcd.com/{0}/info.0.json"


class XKCDService(Service):
    """
    Service that handles anything XKCD comic related (manual comic and daily update checks)

    Parameters
    -----------
    bot: BunkBot
        Base class reference to the bot

    database: DatabaseService
        Base class reference to the database service to update the latest comic id

    config: ConfigService
        Configuration service to read from for the configured channel to send an update

    channel: ChannelService
        Wrapper service to send a new comic
    """
    def __init__(self, bot: BunkBot, database: DatabaseService, config: ConfigService, channels: ChannelService):
        super().__init__(bot, database)
        self.config: ConfigService = config
        self.channels: ChannelService = channels
        self.bot.on_initialized += self._configure_comic_check


    @staticmethod
    async def get_xkcd_comic(ctx: Context) -> any:
        """
        Retrieve a basic XKCD comic based on what the
        user has supplied in the command

        Parameters
        -----------
        ctx: Context
            Discord context to pull out keyword args for the comic

        Returns
        --------
            Result from the XKCD comic API
        """
        p_comic: int = None
        latest: dict = await http_get(XKCD_INFO_URL)

        if ctx is not None:
            params: List[str] = get_cmd_params(ctx)
            if len(params) > 0:
                p_flag = params[0]
                if p_flag.isdigit() and int(p_flag) <= latest["num"]:
                    p_comic = p_flag

        if p_comic is not None:
            return await http_get(XKCD_JSON_URL.format(p_comic))

        return await http_get(XKCD_INFO_URL)


    async def check_new_comic(self) -> None:
        """
        Every day, check for a new XKCD comic. If the id of the comic is newer than
        what was last stored in the database, post it into the configured channel and
        update the database value
        """
        try:
            channel: TextChannel = await self.channels.get_by_name(self.config.xkcd_channel)

            if channel is not None:
                comic = await XKCDService.get_xkcd_comic(None)
                comic_id = "xkcd_{0}".format(comic["num"])
                db_comic_id = self.database.get_comic_by_name(comic_id)
                ids_match = db_comic_id is None or comic_id != db_comic_id["name"]

                if ids_match:
                    self.database.update_comic(comic_id)
                    await channel.send(embed=XKCDService.create_embed_comic(comic))
            else:
                await self.channels.log_warning("Cannot locate channel {0} for XKCD. Aborting.".format(self.config.xkcd_channel))
        except Exception as e:
            await self.channels.log_error(e, "check_new_comic")

        
    @staticmethod
    def create_embed_comic(result: any) -> Embed:
        """
        Create an embedded discord comic from an XKCD API result

        Parameters
        -----------
        result: any
            Result from the XKCD comic API
        """
        embed: Embed = Embed()
        embed.title = result["safe_title"]
        embed.url = "{0}/{1}".format(XKCD_BASE_URL, result["num"])
        embed.set_image(url=result["img"])
        embed.set_footer(text=result["alt"])
        return embed


    async def _configure_comic_check(self) -> any:
        if self.config.xkcd_channel is not None:
            DaemonHelper.add(self.check_new_comic, trigger="cron", hour=10)

