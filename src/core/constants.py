USER_NAME_REGEX: str = r"[^\x00-\x7F]+"
URL_REGEX: str = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
OKWHITE: str = '\033[00m'
OKBLUE: str = '\033[94m'
OKGREEN: str = '\033[92m'
WARNING: str = '\033[93m'
ERROR: str = '\033[91m'
BOLD: str = '\033[1m'


ROLE_ADMIN: str = "admin"
ROLE_MODERATOR: str = "moderator"
ROLE_MODERATOR_PERMS: str = "moderator_perms"
ROLE_GAMING: str = "gaming"
ROLE_STREAMING: str = "streaming"
ROLE_VIP: str = "vip"
ROLE_VIP_PERMS: str = "vip_perms"
