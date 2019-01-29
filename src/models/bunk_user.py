from discord import Member

"""
Simple wrapper class which will take 
an instance of a discord member as 
the primary DI variable
"""
class BunkUser:
    def __init__(self, member: Member) -> None:
        self.member: Member = member

    @property
    def id(self) -> int:
        return self.member.id

    @property
    def name(self) -> str:
        return self.member.name