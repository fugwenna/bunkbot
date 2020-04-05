from ..core.dates import get_now

"""
'Interface' like object to
assist in type mapping
"""
class DatabaseUser:
    def __init__(self, db_user: any):
        self.ref: any = db_user
        self.last_online: str = get_now()
        self.id: int = int(db_user["id"])
        self.level: int = int(db_user["level"])
        self.name: str = db_user["name"]
        self.xp: float = float(db_user["xp"])
        self.was_added: bool = False
        self.is_deleted: bool = False
        self.hangan: HangmanInfo = None

        if (db_user.get("hangman")):
            self.hangman = HangmanInfo(db_user["hangman"])


    def update(self) -> None:
        self.ref["level"] = self.level
        self.ref["xp"] = self.xp
        self.ref["hangman"] = {
            "solo_games_played": self.hangman.solo_games_played,
            "solo_games_won": self.hangman.solo_games_won,
            "random_games_played": self.hangman.random_games_played,
            "random_games_won": self.hangman.random_games_won,
            "other_games_played": self.hangman.other_games_played,
            "other_games_won": self.hangman.other_games_won,
            "games_started": self.hangman.games_started,
            "games_started_won": self.hangman.games_started_won
        }


class HangmanInfo:
    def __init__(self, hangman: any):
        self.solo_games_played = int(hangman["solo_games_played"]),
        self.solo_games_won = int(hangman["solo_games_won"]),
        self.random_games_played = int(hangman["random_games_played"]),
        self.random_games_won = int(hangman["random_games_played"]),
        self.other_games_played = int(hangman["other_games_played"]),
        self.other_games_won = int(hangman["other_games_played"]),
        self.games_started = int(hangman["games_started"]),
        self.games_started_won = int(hangman["games_started_won"])
