from typing import List
from discord import Role, Color

from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_user import BunkUser
from ..core.service import Service
from ..db.database_service import DatabaseService

"""
Service responsible for handling role references
and removing/adding new roles
"""
class RoleService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService, channels: ChannelService):
        super().__init__(bot, database)
        self.admin: Role = None
        self.channels: ChannelService = channels


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
                await ref.delete()
        
        
    # non-event driven - directly add a role when anothoer
    # service has deemed appropriate
    async def add_role(self, role_name: str, user: BunkUser, color: Color = None) -> Role:
        role: Role = None
        roles = user.member.roles.copy()

        if not user.has_role(role_name):
            role = self.get_role(role_name)

            if role is None:
                if color is None:
                    role: Role = await self.bot.server.create_role(name=role_name)
                else: 
                    role: Role = await self.bot.server.create_role(name=role_name, color=color)

            roles.append(role)
            await user.set_roles(roles)

        return role


    # when updating users/roles check for roles which
    # are no longer being used
    async def prune_orphaned_roles(self, pattern: str = None) -> None:
        if self.bot.server is None:
            pass
        else:
            empty_color_roles: List[str] = []
        
            if pattern is None:
                empty_color_roles = [r.name for r in self.bot.server.roles if len(r.members) == 0]
            else:
                empty_color_roles = [r.name for r in self.bot.server.roles if pattern in r.name and len(r.members) == 0]

            for orphan_role in empty_color_roles:
                await self.channels.log_info("Removing role `{0}`".format(orphan_role))
                await self.rm_role(orphan_role)


    # get a role contain a given pattern in the name
    async def get_role_containing(self, pattern: str, user: BunkUser) -> Role:
        role = next((r for r in user.member.roles if pattern in r.name.lower()), None)

        return role
        
    # get the index of a given role (or pattern)
    async def get_lowest_index_for(self, pattern: str) -> int:
        roles: List[int] = [r.position for r in self.bot.server.roles if pattern in r.name]
        roles.sort()

        if len(roles) == 0:
            return 1

        return roles[:1][0]
