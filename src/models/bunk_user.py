from discord import Member
from src.util.dates import get_now


"""
'Interface' like object to
assist in type mapping
"""
class DatabaseUser:
    def __init__(self):
        self.level: int = 0
        self.last_online: str = get_now()


"""
Simple wrapper class which will take 
an instance of a discord member as 
the primary DI variable and maps an existing
database user
"""
class BunkUser:
    def __init__(self, member: Member, db_user: DatabaseUser = None) -> None:
        self.member: Member = member
        self.db_user: DatabaseUser = db_user

    @property
    def id(self) -> int:
        return self.member.id

    @property
    def name(self) -> str:
        return self.member.name

    @property
    def level(self) -> int:
        return self.db_user.level

    @property
    def last_online(self) -> str:
        return self.db_user.last_online
