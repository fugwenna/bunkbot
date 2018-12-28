from ..models.service import Service

"""
Service responsible for anything superuser
related - handles some logic for admin/moderator cogs
"""
class SudoService(Service):
    def __init__(self):
        super().__init__()
        self.SERVER_LOCKED: bool = False