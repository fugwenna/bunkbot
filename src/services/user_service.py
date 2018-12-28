from ..models.service import Service

"""
Service responsible for handling any
bunk user references + syncing with database
"""
class UserService(Service):
    def __init__(self):
        super().__init__()
        self.users: list = []