from discord import Role
from ..bunkbot import BunkBot
from ..models.service import Service
from ..services.database_service import DatabaseService

"""
Service responsible for handling role references
and removing/adding new roles
"""
class RoleService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService):
        super().__init__(bot, database)
        self.admin: Role = None


    async def get_role_containing(self, pattern: str) -> Role:
        return Role()