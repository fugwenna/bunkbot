from src.util.bunk_user import BunkUser

class Poll:
    def __init__(self):
        self.author: BunkUser or None = None
        self.question: str = ""
        self.votes = []
        self.options = []
        self.is_active: bool = False
        self.is_live: bool = False