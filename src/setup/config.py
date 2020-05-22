import json
from os import path
from typing import IO
from tinydb import TinyDB

from ezio import prompt, print_success, print_warning, print_info, OKWHITE
from fs import DEFAULT_CONFIG_PATH, DEFAULT_DB_PATH


"""
Prompt user to create the default *required* configuration, i.e.
channels, roles, db config etc
"""

def _setup_primary_channel(config: dict) -> dict:
    print_info("Primary chat channel required. This is used for new user prompts.")
    config["primary_channel"] = prompt("Enter primary chat channel name: ")
    print_success("Primary chat channel saved: {0}".format(OKWHITE + config["primary_channel"]))
    return config


def _setup_log_channels(config: dict) -> dict:
    return config


def _setup_mod_roles(config: dict) -> dict:
    return config


def _setup_api_keys(config: dict) -> dict:
    return config


def create_config() -> bool:
    if not path.exists(path.realpath(DEFAULT_CONFIG_PATH)):
        with open(DEFAULT_CONFIG_PATH, "w") as f:
            f_config: dict = {}
            f_config = _setup_primary_channel(f_config)
            f_config = _setup_log_channels(f_config)
            f_config = _setup_mod_roles(f_config)
            f_config = _setup_api_keys(f_config)
            f.write(json.dumps(f_config, indent=4))

        return True
    else:
        print_warning("\nConfig file already exists. Exiting.")
        return False
