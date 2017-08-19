from src.util.bunk_user import BunkUser

"""
Wrapper class for dueling
"""
class Duel:
    def __init__(self, challenger, opponent):
        self.challenger: BunkUser = challenger
        self.opponent: BunkUser = opponent