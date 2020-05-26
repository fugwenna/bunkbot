import json
from os import path
from typing import IO

from .ezio import prompt, print_success, print_warning, print_info
from ..core.constants import OKWHITE
from ..etc.config_constants import \
    DEFAULT_CONFIG_PATH, CHANNEL_PRIMARY, CHANNEL_LOGS, \
    TOKEN_DISCORD, KEY_CLEVERBOT, KEY_WEATHER, KEY_TENOR, PATH_DB


"""
Prompt user to create the default *required* configuration, i.e.
channels, roles, db config etc
"""
def _setup_discord_token(config: dict) -> None:
    if config and config.get(TOKEN_DISCORD):
        return

    _get_prompt_for_setup(
        config,
        TOKEN_DISCORD,
        "",
        "Discord developer token required for the bot",
        "Enter Discord developer token: ",
        "Discord token saved"
    )


def _setup_primary_channel(config: dict) -> None:
    if config and config.get(CHANNEL_PRIMARY):
        return

    _get_prompt_for_setup(
        config,
        CHANNEL_PRIMARY,
        "general",
        "Primary chat channel required. This is used for new user prompts.",
        "Enter primary chat channel name {0}".format(OKWHITE + "(default 'general'): "),
        "Primary chat channel saved"
    )


def _setup_log_channels(config: dict) -> None:
    if config and config.get(CHANNEL_LOGS):
        return

    _get_prompt_for_setup(
        config,
        CHANNEL_LOGS,
        "bot-logs",
        "Enter a log channel (bot will log errors/info here).",
        "Log channel {0}".format(OKWHITE + "(default 'bot-logs'): "),
        "Log channel saved"
    )


def _setup_api_keys(config: dict) -> None:
    if not config or not config.get(KEY_CLEVERBOT):
        _get_prompt_for_setup(
            config,
            KEY_CLEVERBOT,
            "",
            "Cleverbot API key for chat capabilities",
            "Enter your API key {0}".format(OKWHITE + "(leave blank to not configure): "),
            "Cleverbot API key saved",
            False
        )

    if not config or not config.get(KEY_WEATHER):
        _get_prompt_for_setup(
            config,
            KEY_WEATHER,
            "",
            "Open weather API key for weather updates",
            "Enter your open weather API key {0}".format(OKWHITE + "(leave blank to not configure): "),
            "Open weather API key saved",
            False
        )

    if not config or not config.get(KEY_TENOR):
        _get_prompt_for_setup(
            config,
            KEY_TENOR,
            "",
            "Tenor API key for sending images in chat/8ball",
            "Enter your tenor API key {0}".format(OKWHITE + "(leave blank to not configure): "),
            "Tenor API key saved",
            False
        )


def _setup_non_prompted_defaults(config: dict) -> None:
    if not config or not config.get(PATH_DB):
        config[PATH_DB] = "./src/db/db.json"


def _get_prompt_for_setup(config: dict, config_prop: str, val: str, info: str, prompt_str: str, success: str, create_default: bool = True) -> None:
    print_info(info)
    config[config_prop] = prompt(prompt_str + OKWHITE)

    if create_default and config[config_prop].strip() == "":
        config[config_prop] = val

    if config[config_prop]:
        print_success("{0}: {1}\n".format(success, OKWHITE + config[config_prop]))
    else:
        print_warning("No configuration set for {0}".format(OKWHITE + config_prop))


def create_config() -> bool:
    print("\n")
    try:
        if not path.exists(DEFAULT_CONFIG_PATH):
            tmp = open(DEFAULT_CONFIG_PATH, "w+")
            tmp.close()

        with open(DEFAULT_CONFIG_PATH, "r+") as f:
            f_config: dict = None

            try:
                f_config = json.load(f)
            except:
                f_config = {}

            _setup_discord_token(f_config)
            _setup_primary_channel(f_config)
            _setup_log_channels(f_config)
            _setup_api_keys(f_config)
            _setup_non_prompted_defaults(f_config)

            f.seek(0)
            f.truncate()
            f.write(json.dumps(f_config, indent=4))

        return True
    except:
        print_warning("\nConfig file could not be created. Exiting.")
        return False
