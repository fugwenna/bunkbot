from typing import List
from discord import Role

from ..bunkbot import BunkBot
from ..core.bunk_user import BunkUser
from ..core.service import Service
from ..db.database_service import DatabaseService

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
        return next((role for role in self.server.roles if role.name == role_name), None)


    # non-event driven - directly remove a role when anothoer
    # service has deemed appropriate
    async def rm_role(self, role_name: str, user: BunkUser = None) -> None:
        if user is not None:
            roles = user.member.roles.copy()
            roles = [r for r in user.member.roles if r.name != role_name]
            await user.set_roles(roles)
        else:
            roles: List[Role] = [r for r in self.bot.server.roles.copy() if r.name == role_name]
            for role in roles:
                ref: Role = role
                ref.remove()
        
        
    # non-event driven - directly add a role when anothoer
    # service has deemed appropriate
    async def add_role(self, role_name: str, user: BunkUser) -> None:
        roles = user.member.roles.copy()

        if not user.has_role(role_name):
            roles.append(self.get_role(role_name))
            await user.set_roles(roles)


    # get a role contain a given pattern in the name
    async def get_role_containing(self, pattern: str, user: BunkUser) -> Role:
        role = next((r for r in user.member.roles if pattern in r.name.lower()), None)

        return role


    # when updating users/roles check for roles which
    # are no longer being used
    async def prune_orphaned_roles(self, pattern: str = None) -> None:
        empty_color_roles: List[str] = []
        
        if pattern is None:
            empty_color_roles = [r.name for r in self.bot.server.roles if len(r.members) == 0]
        else:
            empty_color_roles = [r.name for r in self.bot.server.roles if pattern in r.name and len(r.members) == 0]

        for orphan_role in empty_color_roles:
            await self.roles.rm_role(orphan_role)