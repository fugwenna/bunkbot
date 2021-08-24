from typing import List
from discord import Role, Color, role

from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_user import BunkUser
from ..core.service import Service
from ..db.database_service import DatabaseService

class RoleService(Service):
    """
    Service responsible for handling role references
    and removing/adding new roles

    Parameters
    -----------
    bot: Bunkbot
        Super class instance of the bot

    database: DatabaseService
        Super class instance of the database service

    channels: ChannelService
        Access to the server channels and other channel functions
    """
    def __init__(self, bot: BunkBot, database: DatabaseService, channels: ChannelService):
        super().__init__(bot, database)
        self.admin: Role = None
        self.channels: ChannelService = channels


    def get_role(self, role_name: str) -> Role:
        """
        Get a role directly from the server by name

        Parameters
        -----------
        role_name: str
            Name of the role to retrieve from the server
        """
        return next((role for role in self.server.roles if role.name == role_name), None)

        
    def get_role_by_pattern(self, pattern: str, roles: List[Role] = None) -> Role:
        """
        Get a role directly from the server with a pattern "contains"

        Parameters
        -----------
        pattern: str
            Pattern which will be used to fuzzy search a role name

        roles: List[Role] (optional)
            Optional list of roles to search if the default server is not used
        """
        if roles is None:
            roles = self.server.roles

        return next((role for role in roles if pattern in role.name), None)


    async def rm_role(self, role_name: str, user: BunkUser = None) -> None:
        """
        Non-event driven - directly remove a role when another service has deemed appropriate

        Parameters
        -----------
        role_name: str
            Name of the role to remove

        user: Bunkuser (optional)
            When supplied, the role will be removed from a user rather than the server list
        """
        if user is not None:
            roles = user.member.roles.copy()
            roles = [r for r in user.member.roles if r.name != role_name]
            await user.set_roles(roles)
        else:
            roles: List[Role] = [r for r in self.bot.server.roles.copy() if r.name == role_name]
            for role in roles:
                ref: Role = role
                await ref.delete()
        

    async def rm_roles_from_user(self, role_names: List[str], user: BunkUser) -> None:
        """
        Non-event driven - directly remove a role when another service has deemed appropriate

        Parameters
        -----------
        role_names: List[str]
            List of the roles to remove

        user: Bunkuser 
            User from which the roles will be removed from a user 
        """
        roles: List[Role] = user.member.roles.copy()
        new_roles: List[Role] = [r for r in roles if not r.name not in roles_to_rm]

        await user.set_roles(new_roles)

        
    async def add_role_to_user(self, role_name: str, user: BunkUser, color: Color = None) -> Role:
        """
        Non-event driven - directly add a role when another service has deemed appropriate

        Parameters
        -----------
        role_name: str
            Name of the role to add

        user: BunkUser
            User which to add the role

        color: Color (optional)
            Optionally add a color to the role

        Returns
        --------
        Role added to the user
        """
        roles: List[Role] = await self._get_user_roles_to_set(user.member.roles.copy(), role_name, user, color)
        await user.set_roles(roles)

        return self.get_role(role_name)


    async def add_roles_to_user(self, role_names: List[str], user: BunkUser, color: Color = None) -> List[Role]:
        """
        Non-event driven - directly add multiple roles when another service has deemed appropriate

        Parameters
        -----------
        role_names: List[str]
            List of roles to add to the user

        user: BunkUser
            User which to add the roles

        color: Color (optional)
            Optionally add a color to the roles

        Returns
        --------
        Roles added to the user
        """
        roles = user.member.roles.copy()
        for role_name in role_names:
            roles = await self._get_user_roles_to_set(roles, role_name, user, color)

        await user.set_roles(roles)
        return roles


    async def _get_user_roles_to_set(self, current_roles: List[Role], role_name: str, user: BunkUser, color: Color = None) -> List[Role]:
        if not user.has_role(role_name):
            role = self.get_role(role_name)

            if role is None:
                if color is None:
                    role: Role = await self.bot.server.create_role(name=role_name)
                else: 
                    role: Role = await self.bot.server.create_role(name=role_name, color=color)

            current_roles.append(role)
        return current_roles


    def _get_user_roles_to_rm(self, role_name: str, user: BunkUser) -> List[Role]:
        roles_to_rm: List[Role] = []
        if user.has_role(role_name):
            role = self.get_role(role_name)
            roles_to_rm.append(role)

        return roles_to_rm


    async def prune_orphaned_roles(self, pattern: str = None) -> None:
        """
        When updating users/roles check for roles which are no longer being used

        Parameters
        -----------
        pattern: str (optional)
            Only pruned orphaned roles that contain a specific pattern in the name
        """
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


    async def get_role_containing(self, pattern: str, user: BunkUser) -> Role:
        """
        Get a user role that contains a given pattern in the name

        Parameters
        -----------
        pattern: str
            Pattern which the role name must contain

        user: BunkUser
            User which to find the role
        """
        role = next((r for r in user.member.roles if pattern in r.name.lower()), None)

        return role
        
    async def get_lowest_index_for(self, pattern: str) -> int:
        """
        Get the server role index of a given role name (pattern)

        Parameters
        -----------
        pattern: str
            Pattern which to locate a role by it's index
        """
        roles: List[int] = [r.position for r in self.bot.server.roles if pattern in r.name]
        roles.sort()

        if len(roles) == 0:
            return 1

        return roles[:1][0]
