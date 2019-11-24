from ..util.dates import get_now

"""
'Interface' like object to
assist in type mapping
"""
class DatabaseUser:
    def __init__(self, db_user: any):
        self.last_online: str = get_now()
        self.id: int = int(db_user["id"])
        self.level: int = int(db_user["level"])
        self.name: str = db_user["name"]
        self.xp: float = float(db_user["xp"])
        self.was_added: bool = False
