from discord import TextChannel, Message

from ..core.bunk_user import BunkUser

"""
Base model for custom games with
some basic methods built in
"""
class CustomGame:
    def __init__(self, channel: TextChannel, creator: BunkUser):
        self.channel: TextChannel = channel
        self.creator: BunkUser = creator
        self.set_defaults()


    def set_defaults(self) -> None:
        self.is_win: bool = False
        self.is_loss: bool = False
        self.is_cancelled: bool = False
        self.is_complete: bool = False


    async def is_cancel(self, msg: Message, game_creator: BunkUser) -> bool:
        if msg.author.id == game_creator.id:
            l_content: str = msg.content.lower()
            if l_content == "cancel" or l_content == "exit":
                self.is_cancelled = True
                await self.cancel_game()
                return True

        return False


    def get_content(self, msg: Message) -> None:
        return msg.content.lower()

        
    async def cancel_game(self) -> None:
        await self.channel.delete()


    async def update(self, message: Message, user: BunkUser) -> None:
        pass


    async def start(self) -> None:
        pass
