from discord import Message
from ..core.dates import get_now
from ..core.functions import is_stupid_mkr
from ..core.service import Service


class TimeService(Service):
    async def get_time(self, message: Message) -> None:
        time = get_now()

        if is_stupid_mkr(message.author.name):
            time += ", you idiot"

        return time
