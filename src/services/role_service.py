from discord import Role
from ..models.service import Service
from ..bunkbot import BunkBot

"""
Service responsible for handling role references
and removing/adding new roles
"""
class RoleService(Service):
    def __init__(self, bot: BunkBot):
        super().__init__(bot)
        self.admin: Role = None


    async def get_role_containing(self, pattern: str) -> Role:
        return Role()