from typing import List
from discord.ext.commands import Context

from ..bunkbot import BunkBot
from ..core.bunk_exception import BunkException
from ..core.bunk_user import BunkUser
from ..core.functions import get_cmd_params
from ..core.service import Service
from ..db.database_service import DatabaseService
from ..user.user_service import UserService
from .duel import Duel
from .duel_result import DuelResult


"""
Offloadable logic into this service for RPG related cogs
"""
class RpgService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService, users: UserService):
        super().__init__(bot, database)
        self.users: UserService = users
        self.duels: List[Duel] = []


    # duel another user in the server
    async def challenge_duel(self, ctx: Context) -> Duel:
        chal: BunkUser = None
        opnt: BunkUser = None
        names: List[str] = get_cmd_params(ctx)
        is_bot_challenge: bool = False

        if len(names) == 0:
            raise BunkException("Please enter an opponents name to duel")
        else:
            name = names[0].lower()
            chal = self.users.get_by_id(ctx.message.author.id)
            is_bot_challenge = name == self.bot.name_lower
            
            if is_bot_challenge:
                opnt = BunkUser(self.bot.member_ref, None)
            else:
                opnt = self.users.get_by_username(name)

            if opnt is None:
                raise BunkException("Cannot locate user {0}".format(name))

            if name == chal.name:
                raise BunkException("You can't duel yourself, dingus")

        self.set_challenged(chal, opnt)
        self.remove_duel(chal, False)

        duel = Duel(chal, opnt)
        duel.is_bot_challenge = is_bot_challenge
        self.duels.append(duel)

        return duel


    # check if the two users are currently in other duels
    @staticmethod
    def set_challenged(chal: BunkUser, opnt: BunkUser) -> None:
        if chal.is_dueling:
            raise BunkException("{0} is currently in a duel".format(chal.name))

        if opnt.is_dueling:
            raise BunkException("{0} is currently in a duel".format(opnt.name))

        opnt.challenged_by_id = chal.id


    # accept a duel if the user is challenged
    def accept_duel(self, user: BunkUser) -> DuelResult:
        is_bot_duel: bool = user.id == self.bot.user.id 

        if not is_bot_duel and not user.challenged_by_id:
            raise BunkException("You have no duels to accept")

        duel: Duel = None

        if is_bot_duel:
            duel = next((d for d in self.duels if d.opponent.id == user.id), None)
        else:
            duel = next((d for d in self.duels if d.opponent.id == user.id and d.challenger.id == user.challenged_by_id), None)

        if duel is None:
            raise BunkException("Error executing duel :(")

        self.remove_duel(user, True)

        return duel.execute()


    # reject a duel if the user is challenged
    def reject_duel(self, user: BunkUser) -> bool:
        if not user.challenged_by_id:
            raise BunkException("You have no duels to reject")

        self.remove_duel(user, True)
        return True


    # remove ref of duel 
    def remove_duel(self, user: BunkUser, opnt: bool) -> None:
        duel: Duel = None

        if opnt:
            duel = next((d for d in self.duels if d.opponent.id == user.id), None)
        else:
            duel = next((d for d in self.duels if d.challenger.id == user.id), None)

        if duel is not None:
            self.duels.remove(duel)

        user.challenged_by_id = None
    