from tinydb import TinyDB, Query
from tinydb.database import Table
from discord import Member
from discord import Game
from ..bunkbot import BunkBot
from ..models.service import Service
from ..models.database_user import DatabaseUser
from ..util.constants import DB_SERVER_ID, DB_PATH, DB_CONFIG, DB_USERS, DB_RPG, DB_HOLIDAYS, DB_STREAMS, DB_GAMES
from ..util.functions import simple_string

CONFIG = Query()

"""
Injectable service used for accessing the local database
"""
class DatabaseService(Service):
    def __init__(self, bot: BunkBot):
        super().__init__(bot)
        self.db = TinyDB(DB_PATH)
        self.config: Table = self.db.table(DB_CONFIG)
        self.users: Table = self.db.table(DB_USERS)
        self.rpg: Table = self.db.table(DB_RPG)
        self.holidays: Table = self.db.table(DB_HOLIDAYS)
        self.streams: Table = self.db.table(DB_STREAMS)
        self.game_names: Table = self.db.table(DB_GAMES)
        self.server = self.bot.get_server(self.get(DB_SERVER_ID))

    # helper method that will query the requested table
    # and property name - default table as config
    def get(self, attr: str) -> str or None:
        res = self.config.get(CONFIG[attr] != "")
        if res is not None:
            return res[attr]
        else:
            return None

    # get a user by the passed discord member reference - this should
    # only be used when loading a user once - either at bot load, or
    # new users
    def get_user_by_member_ref(self, member: Member) -> DatabaseUser:
        db_user = self.users.get(Query().id == member.id)
        if db_user is None:
            print("can't find " + member.name)
            #self.users.insert({
            #    "name": simple_string(member.name),
            #    "member_name": member.name,
            #    "id": member.id,
            #    "xp": 0,
            #    "level": 1
            #})

            db_user = self.users.get(Query().id == member.id)

        user = DatabaseUser(db_user)

        return user

    # try to locate a relatively unique game when a user
    # starts playing a random game - if the game does not
    # exist, add it to the database
    def collect_game(self, game: Game) -> any:
        db_game = self.game_names.get(Query().name == game.name)

        if db_game is None:
            self.game_names.insert({"name": game.name, "type": game.type})

        return db_game