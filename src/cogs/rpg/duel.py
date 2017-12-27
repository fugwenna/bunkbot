from src.cogs.rpg.rpg_exception import RPGException
from src.util.helpers import roll

"""
Duel wrapper class
"""
class Duel:
    def __init__(self, challenger, opponent):
        if challenger.duel is not None:
            if challenger.duel.pending or challenger.duel.active:
                raise RPGException("You are already dueling {0}. Type !cancel to cancel this duel".format(challenger.duel.opponent.name))

        if opponent.duel is not None:
            if opponent.duel.pending or opponent.duel.active:
                raise RPGException("{0} is currently dueling {1}".format(opponent.name, opponent.duel.opponent.name))

        if challenger == opponent:
            raise RPGException("You can't duel yourself, loser")

        self.pending = True
        self.active = False
        self.challenger = challenger
        self.opponent = opponent
        self.winner = None
        self.loser = None
        self.tie = False


    # when a duel is accepted by the
    # opponent user, execute it and fire
    # the on_duel_executed event
    async def execute(self) -> None:
        self.active = True
        self.pending = False

        self.challenger.duel_roll = roll()
        self.opponent.duel_roll = roll()

        self.challenger.duel = None
        self.opponent.duel = None

        if self.challenger.duel_roll == self.opponent.duel_roll:
            self.tie = True
        else:
            if self.challenger.duel_roll > self.opponent.duel_roll:
                self.winner = self.challenger
                self.loser = self.opponent
            else:
                self.winner = self.opponent
                self.loser = self.challenger

            #self.winner = self.challenger if self.challenger.duel_roll > self.opponent.duel_roll else self.opponent
            #self.loser = self.challenger if self.challenger.duel_roll < self.opponent.duel_roll else self.opponent


    # after a duel, update each individual
    # xp gain
    async def update_xp(self):
        return