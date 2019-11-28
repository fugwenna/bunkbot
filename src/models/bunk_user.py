from discord import Member

from .database_user import DatabaseUser
from ..util.functions import simple_string
from ..util.constants import ROLE_ADMIN, ROLE_MODERATOR_PERMS, ROLE_VIP_PERMS

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
    def level(self) -> int:
        return self.db_user.level


    @property
    def last_online(self) -> str:
        return self.db_user.last_online


    @property
    def is_gaming(self) -> bool:
        if not self.member:
            return False

        return self.member.game is not None and self.member.game.type == 0


    @property
    def is_streaming(self) -> bool:
        if not self.member:
            return False

        return self.member.game is not None and self.member.game.type == 1


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