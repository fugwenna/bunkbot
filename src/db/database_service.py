from discord import Member, Game, Guild
from tinydb import TinyDB, Query
from tinydb.database import Table

from .database_user import DatabaseUser
from ..core.bunk_user import BunkUser
from ..core.bunk_exception import BunkException
from ..core.constants import DB_SERVER_ID, DB_PATH, DB_CONFIG, DB_USERS, DB_RPG, DB_HOLIDAYS, DB_STREAMS, DB_GAMES, DB_TOKEN, DB_TENOR
from ..core.error_log_service import ErrorLogService
from ..core.functions import simple_string
from ..bunkbot import BunkBot

"""
Injectable service used for accessing the local database
"""
class DatabaseService:
    def __init__(self, bot: BunkBot, logger: ErrorLogService):
        self.bot: BunkBot = bot
        self.logger: ErrorLogService = logger
        self.db: TinyDB = TinyDB(DB_PATH)
        self.config: Table = self.db.table(DB_CONFIG)
        self.users: Table = self.db.table(DB_USERS)
        self.rpg: Table = self.db.table(DB_RPG)
        self.holidays: Table = self.db.table(DB_HOLIDAYS)
        self.streams: Table = self.db.table(DB_STREAMS)
        self.game_names: Table = self.db.table(DB_GAMES)
        self.bot.on_initialized += self.set_bot_props
        self.set_defaults()


    async def set_bot_props(self) -> None:
        self.server: Guild = self.bot.get_guild(self.get(DB_SERVER_ID, False))

    
    def set_defaults(self) -> None:
        token = self.config.get(Query()["token"] != "", 1)
        if token is None:
            self.config.insert({"token": ""})

        srv = self.config.get(Query()["serverid"] != "", 2)
        if srv is None:
            self.config.insert({"serverid": ""})


    # helper method that will query the requested table
    # and property name - default table as config
    def get(self, attr: str, throw: bool = True) -> str or None:
        res = self.config.get(Query()[attr] != "")

        if res is not None:
            return res[attr]
        else:
            if throw:
                err: str = "Unknown database value for '{0}'. You must supply a value in the 'src/db/db.json' config entity property '{0}'".format(attr)
                raise BunkException(err)


    # get a user by the passed discord member reference - this should
    # only be used when loading a user once - either at bot load, or
    # new users
    def get_user_by_member_ref(self, member: Member) -> DatabaseUser:
        is_being_added: bool = False
        db_user = self.users.get(Query().id == member.id)

        if not member.bot and db_user is None:
            self.users.insert({
                "name": simple_string(member.name),
                "member_name": member.name,
                "id": member.id,
                "xp": 0,
                "level": 1
            })

            db_user = self.users.get(Query().id == member.id)
            is_being_added = True

        # ignore bot users
        user: DatabaseUser = None
        if db_user is not None:
            user = DatabaseUser(db_user)

        if user is not None:
            user.was_added = is_being_added

        if db_user is not None and not db_user.get("hangman"):
            db_user["hangman"] = {
                "solo_games_played": 0,
                "solo_games_won": 0,
                "random_games_played": 0,
                "random_games_won": 0,
                "other_games_played": 0,
                "other_games_won": 0,
                "games_started": 0,
                "games_started_won": 0
            }

            self.users.upsert(db_user, Query().id == member.id)
            user = DatabaseUser(db_user)

        return user


    def update_user(self, user: DatabaseUser) -> None:
        user.update()
        self.users.upsert(user.ref, Query().id == user.id)


    # try to locate a relatively unique game when a user
    # starts playing a random game - if the game does not
    # exist, add it to the database
    def collect_game(self, game: Game) -> bool:
        added: bool = False
        db_game = self.game_names.get(Query().name == game.name)

        if db_game is None:
            self.game_names.insert({
                "name": game.name, 
                "type": game.type
            })
            added = True

        return added
