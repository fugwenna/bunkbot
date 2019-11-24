from discord import Role
from ..bunkbot import BunkBot
from ..models.bunk_user import BunkUser
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


    # get a role directly from the server
    def get_role(self, role_name: str) -> Role:
        return next(role for role in self.database.server.roles if role.name == role_name)


    # non-event driven - directly update a role when anothoer
    # service has deemed appropriate
    async def rm_role(self, user: BunkUser, role_name: str) -> None:
        roles = user.member.roles.copy()
        roles = [r for r in user.member.roles if r.name != role_name]
        await self.bot.replace_roles(user.member, *roles)
        

    async def add_role(self, user: BunkUser, role_name: str) -> None:
        roles = user.member.roles.copy()
        roles.append(self.get_role(role_name))
        await self.bot.replace_roles(user.member, *roles)


    async def get_role_containing(self, pattern: str) -> Role:
        return Role()