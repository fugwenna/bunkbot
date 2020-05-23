import json
from os import path
from typing import IO

from .ezio import prompt, print_success, print_warning, print_info
from ..core.constants import OKWHITE
from ..etc.config_constants import DEFAULT_CONFIG_PATH, CHANNEL_PRIMARY, CHANNEL_LOGS


"""
Prompt user to create the default *required* configuration, i.e.
channels, roles, db config etc
"""

def _setup_primary_channel(config: dict) -> dict:
    if config and config.get(CHANNEL_PRIMARY):
        return config

    return _get_prompt_for_setup(
        config,
        CHANNEL_PRIMARY,
        "general",
        "Primary chat channel required. This is used for new user prompts.",
        "Enter primary chat channel name {0}".format(OKWHITE + "(default 'general'): "),
        "Primary chat channel saved"
    )


def _setup_log_channels(config: dict) -> dict:
    if config and config.get(CHANNEL_LOGS):
        return config

    return _get_prompt_for_setup(
        config,
        CHANNEL_LOGS,
        "bot-logs",
        "Enter a log channel (bot will log errors/info here).",
        "Log channel {0}".format(OKWHITE + "(default 'bot-logs'): "),
        "Log channel saved"
    )


def _setup_mod_roles(config: dict) -> dict:
    return config


def _setup_api_keys(config: dict) -> dict:
    return config


def _get_prompt_for_setup(config: dict, config_prop: str, val: str, info: str, prompt_str: str, success: str) -> dict:
    print_info(info)
    config[config_prop] = prompt(prompt_str)

    if (config[config_prop].strip() == ""):
        config[config_prop] = val

    print_success("{0}: {1}\n".format(success, OKWHITE + config[config_prop]))
    return config


def create_config() -> bool:
    print("\n")
    try:
        with open(path.realpath(DEFAULT_CONFIG_PATH), "r+") as f:
            f_config: dict = None

            try:
                f_config = json.load(f)
            except:
                f_config = {}

            f_config = _setup_primary_channel(f_config)
            f_config = _setup_log_channels(f_config)
            f_config = _setup_mod_roles(f_config)
            f_config = _setup_api_keys(f_config)
            f.seek(0)
            f.truncate()
            f.write(json.dumps(f_config, indent=4))

        return True
    except Exception as e:
        print_warning("\nConfig file could not be created. Exiting.")
        return False
