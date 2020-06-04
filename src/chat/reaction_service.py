import requests, json
from discord import Message, Guild, Emoji
from random import randint

from ..bunkbot import BunkBot
from ..core.http import http_get


DEFAULT_LIST: str = "https://gist.githubusercontent.com/Vexs/629488c4bb4126ad2a9909309ed6bd71/raw/416403f7080d1b353d8517dfef5acec9aafda6c3/emoji_map.json"


class ReactionService():
    def __init__(self, bot: BunkBot):
        self.bot: BunkBot = bot
        self.bot.on_user_message += self.react_to_message
        self.bot.on_initialized += self.get_default_list


    async def get_default_list(self) -> None:
        try:
            self.default_emojis: dict = json.loads(requests.get(DEFAULT_LIST).content)
            self.default_list: list = list(self.default_emojis.keys())
        except:
            self.default_list = []


    async def react_to_message(self, message: Message) -> None:
        if not message.author.bot:
            react: bool = randint(0, 100) <= 10

            if react:
                try:
                    emoji = None
                    use_custom = randint(0, 100) >= 40 or len(self.default_list) == 0 

                    if use_custom:
                        emoji = await self._get_custom_emoji()
                    else:
                        emoji = "{0}".format(self.default_emojis[self.default_list[randint(0,len(self.default_list)-1)]])
                except:
                    emoji = await self._get_custom_emoji()

                if emoji is not None:
                    await message.add_reaction(emoji)

    
    async def _get_custom_emoji(self) -> Emoji:
        g: Guild = self.bot.server
        emotes = await g.fetch_emojis()
        return emotes[randint(0, len(emotes)-1)]
