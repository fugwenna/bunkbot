from typing import List
from discord import Embed
from discord.ext.commands import command, Context, Cog
from random import randint, random, choice
from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_user import BunkUser
from ..core.functions import get_cmd_params
from ..core.registry import USER_SERVICE, CHANNEL_SERVICE, DATABASE_SERVICE
from ..user.user_service import UserService
from ..db.database_service import DatabaseService
from ..core.constants import DB_TENOR
import requests
import json
import urllib.request,urllib.parse,urllib.error
import pprint

ROLE_DESCRIPTION: str = """eightball gives a random GIF fortune for any question asked.\n
    Example: !eightball Will I win the Lottery?
    Example: !8ball Will I ever be a real boy?
"""
class eightball(Cog):
    def __init__(self, channels: ChannelService, users: UserService, database: DatabaseService):
        self.database: DatabaseService = database
        self.channels: ChannelService = channels
        self.users: UserService = users
        self.api_key: str = database.get(DB_TENOR)

    @command(help=ROLE_DESCRIPTION, aliases=["8ball"])
    async def eightball(self, ctx: Context) -> None:
        try:
            await ctx.trigger_typing()
            answers = ["Yes","No","Maybe","I don't know","IDK","Fuck No", "YAS","Snap", "why not", "Whatever","For Sure", "smile", "fortune",
                       "wink", "fart","omg","awkward","suprised","clapping","sigh","scared","sad","confused","cry","lol", "kevin", "kidding",
                       "shit","yass", "annoy", "annoyed", "nah","no way","un huh","excited", "cheer", "beer", "cheers",
                       "no worries","yas bitch", "rage","sorry","ok","love",]
            lmt = 6
            r = requests.get("https://api.tenor.com/v1/anonid?key=%s" % self.api_key)

            if r.status_code == 200:
                anon_id = json.loads(r.content)["anon_id"]
            else:
                anon_id = ""
            search_term = choice(answers)
            r = requests.get(
                "https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s&anon_id=%s" %   
                 (search_term, self.api_key, lmt, anon_id))

            if r.status_code == 200:
                top_8gifs = json.loads(r.content)
                imglist = []
                for i in range(len(top_8gifs['results'])):
                        url = top_8gifs['results'][i]['media'][0]['gif']['url'] 
                        imglist.append(url)
            else:
                top_8gifs = None

            await ctx.send(choice(imglist))
        except Exception as e:
            await self.channels.log_error(e, "eightball")

def setup(bot: BunkBot) -> None:
    bot.add_cog(eightball(CHANNEL_SERVICE, USER_SERVICE,DATABASE_SERVICE))
