USER_NAME_REGEX: str = r"[^\x00-\x7F]+"
URL_REGEX: str = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
OKWHITE: str = '\033[00m'
OKBLUE: str = '\033[94m'
OKGREEN: str = '\033[92m'
WARNING: str = '\033[93m'
ERROR: str = '\033[91m'
BOLD: str = '\033[1m'


##############################################
CHANNEL_CUSTOM_GAMES: str = "custom-games"

DB_PATH: str = "src/db/db.json"
DB_CONFIG: str = "config"
DB_USERS: str = "users"
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
