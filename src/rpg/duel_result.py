from ..core.bunk_user import BunkUser

"""
Metadata class for easy embeds when a duel has completed
"""
class DuelResult:
    def __init__(self, chal: BunkUser, opnt: BunkUser, winner: BunkUser):
        self.challenger: BunkUser = chal
        self.opponent: BunkUser = opnt
        self.winner: BunkUser = winner

        self.challenger.is_dueling = False
        self.challenger.challenged_by_id = None
        self.opponent.is_dueling = False
        self.opponent.challenged_by_id = None
