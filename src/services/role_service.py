from discord import Role

from .database_service import DatabaseService
from ..bunkbot import BunkBot
from ..models.bunk_user import BunkUser
from ..models.service import Service

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
        return next(role for role in self.server.roles if role.name == role_name)


    # non-event driven - directly remove a role when anothoer
    # service has deemed appropriate
    async def rm_role(self, user: BunkUser, role_name: str) -> None:
        roles = user.member.roles.copy()
        roles = [r for r in user.member.roles if r.name != role_name]
        await user.set_roles(roles)
        
        
    # non-event driven - directly add a role when anothoer
    # service has deemed appropriate
    async def add_role(self, user: BunkUser, role_name: str) -> None:
        roles = user.member.roles.copy()

        if not user.has_role(role_name):
            roles.append(self.get_role(role_name))
            await user.set_roles(roles)


    async def get_role_containing(self, pattern: str) -> Role:
        return Role()