"""
Similar to XP progress bar
"""
class PollResultBar:
    def __init__(self, count: int, total: int):
        self.pct = count/total

    def draw(self) -> str:
        bar: list = []
        for i in range(0, 20):
            bar.append("▯")

        pct_rounded = int(self.pct * 10) * 2

        for p in range(0, pct_rounded):
            if p < 20:
                bar[p] = "▮"

        return "".join(bar)