from ..models.service import Service
from ..bunkbot import BunkBot

"""
Service responsible for anything superuser
related - handles some logic for admin/moderator cogs
"""
class SudoService(Service):
    def __init__(self, bot: BunkBot):
        super().__init__(bot)
        self.SERVER_LOCKED: bool = False