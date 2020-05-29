from ..core.bunk_user import BunkUser
from ..core.functions import roll_int
from .duel_result import DuelResult

"""
Class that represents a duel between two bunk_users
"""
class Duel:
    def __init__(self, challenger: BunkUser, opponent: BunkUser):
        self.challenger: BunkUser = challenger
        self.opponent: BunkUser = opponent


    # Execute the duel and return the winner
    def execute(self) -> DuelResult:
        chal_val: int = roll_int()
        opnt_val: int = roll_int()

        winner: BunkUser = None
        loser: BunkUser = None

        if chal_val > opnt_val:
            winner = self.challenger
            loser = self.opponent
        else:
            winner = self.opponent
            loser = self.challenger
        
        result: DuelResult = DuelResult(self.challenger, self.opponent, winner, loser)
        result.challenger_roll = chal_val
        result.opponent_roll = opnt_val

        return result
