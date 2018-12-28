from discord import Channel
from .bunk_user import BunkUser


class BunkbotConversation:
    def __init__(self, initiator: BunkUser, channel: Channel):
        self.chat_timer = 9
        self.last_message_at = -1
        self.initiator = initiator
        self.channel = channel
