from typing import List
from discord import Member, Role, ActivityType, Color

from .constants import ROLE_ADMIN, ROLE_MODERATOR_PERMS, ROLE_VIP_PERMS
from .functions import simple_string
from ..db.database_user import DatabaseUser

"""
Simple wrapper class which will take 
an instance of a discord member as 
the primary DI variable and maps an existing
database user
"""
class BunkUser:
    def __init__(self, member: Member, db_user: DatabaseUser) -> None:
        self.member: Member = member
        self.db_user: DatabaseUser = db_user


    @property
    def id(self) -> int:
        return self.member.id


    @property
    def name(self) -> str:
        return simple_string(self.member.name)


    @property
    def full_name(self) -> str:
        return self.member.name


    @property
    def mention(self) -> str:
        return self.member.mention


    @property
    def color(self) -> Color:
        if not self.member:
            return "Unknown"

        return self.member.color


    @property
    def level(self) -> int:
        return self.db_user.level


    @property
    def last_online(self) -> str:
        return self.db_user.last_online


    @property
    def is_gaming(self) -> bool:
        if not self.member:
            return False

        return next((a for a in self.member.activities if a.type == ActivityType.playing), None) is not None


    @property
    def is_streaming(self) -> bool:
        if not self.member:
            return False

        return next((a for a in self.member.activities if a.type == ActivityType.streaming), None) is not None


    @property
    def is_admin(self) -> bool:
        if self.member is None:
            return False

        return self.has_role(ROLE_ADMIN)


    @property
    def is_moderator(self) -> bool:
        if self.member is None:
            return False

        return self.has_role(ROLE_MODERATOR_PERMS) or self.is_admin


    @property
    def is_vip(self) -> bool:
        if self.member is None:
            return False

        return self.has_role(ROLE_VIP_PERMS)


    def has_role(self, role: str) -> bool:
        return len([r for r in self.member.roles if r.name == role]) > 0


    async def set_roles(self, roles: List[Role]) -> None:
        await self.member.edit(roles=roles)