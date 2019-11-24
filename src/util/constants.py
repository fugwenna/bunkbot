USER_NAME_REGEX = r"[^\x00-\x7F]+"
URL_REGEX = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

CHANNEL_BOT_LOGS: str = "bot-logs"
CHANNEL_BOT_TESTING: str = "bot-testing"
CHANNEL_GENERAL: str = "general"
CHANNEL_GAMING: str = "gaming"
CHANNEL_HOTS: str = "hots"
CHANNEL_MOD_CHAT: str = "mod-chat"
CHANNEL_VIP_CHAT: str = "vip-chat"
CHANNEL_WEATHER: str = "weather"
CHANNEL_STREAMS: str = "streams"
CHANNEL_NEW_USERS: str = "new-user-log"

DB_PATH: str = "src/storage/db.json"
DB_TOKEN: str = "token"
DB_CLEVERBOT: str = "cleverbot"
DB_SERVER_ID: str = "serverid"
DB_WEATHER: str = "weather"
DB_TWITCH_ID: str = "twitch_id"
DB_TWITCH_SECRET: str = "twitch_secret"
DB_CONFIG: str = "config"
DB_USERS: str = "users"
DB_RPG: str = "rpg"
DB_HOLIDAYS: str = "holiday"
DB_STREAMS: str = "streams"
DB_GAMES: str = "game_names"

ROLE_ADMIN: str = "admin"
ROLE_MODERATOR: str = "moderator"
ROLE_MODERATOR_PERMS: str = "moderator_perms"
ROLE_NEW: str = "new"
ROLE_GAMING: str = "gaming"
ROLE_STREAMING: str = "streaming"
ROLE_VIP: str = "vip"
ROLE_VIP_PERMS: str = "vip_perms"
ROLE_BUNKBOT: str = "bunky"

ROLE_MAX: int = 250
ROLE_MAX_PRIMARY: int = 11
ROLE_MAX_COLORS: int = 150
ROLE_MAX_CHANNELS: int = 50
