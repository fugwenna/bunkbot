from src.util.bunk_user import BunkUser
from src.util.helpers import calc_req_xp
from src.storage.db import database

"""
Create a progress bar for the current
user's level
"""
class ProgressBar:
    def __init__(self, user: BunkUser):
        self.pct = 0
        self.user: BunkUser = user


    # draw the progress bar using
    # hollow and filled blocks, and set
    # misc properties (pct)
    def draw(self) -> str:
        # todo fix
        if self.user.xp == 0 and self.user.level == 1:
            bar: list = []
            self.pct = 0.0
            for i in range(0, 20):
                bar.append("▯")
            return "".join(bar)

        now_xp = self.user.xp

        # xp required for the current level
        prev_xp = calc_req_xp(self.user.level)

        # xp required for the next level
        req_xp = calc_req_xp(self.user.next_level)

        # difference from the previous
        # required xp to the current user xp
        from_xp = round(now_xp - prev_xp, 2)

        # difference from the previous
        # required xp to the next level xp
        to_xp = round(req_xp - prev_xp, 2)

        # percentage to the next level calculated by
        # a ratio of the previous xp requirement to the next
        pct = from_xp / to_xp
        pct_rounded = int(round(pct, 1) * 10) * 2

        bar: list = []
        for i in range(0, 20):
            bar.append("▯")

        # todo - this is for my bad code!
        # this shouldnt happen loool
        if pct_rounded - 1 > 20:
            needed_xp = calc_req_xp(self.user.next_level)
            if self.user.xp > needed_xp:
                database.update_user_level(self.user.name)
        else:
            for p in range(0, pct_rounded - 1):
                bar[p] = "▮"

        self.pct = round(pct * 100, 2)

        return "".join(bar)