from discord import Role
from ..models.service import Service

"""
Service responsible for handling role references
and removing/adding new roles
"""
class RoleService(Service):
    def __init__(self):
        super().__init__()
        self.admin: Role = None