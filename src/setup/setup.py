from .config import create_config
from .ezio import print_success, prompt
from ..core.constants import OKWHITE, OKGREEN


"""
This is the primary setup file for the bot. This is to be ran once after the user 
first clones the project so that the specific channels/roles/constants can be defined
within a config.json file (this is not the same as db.json)
"""

if __name__ == "__main__":
    do_setup: bool = prompt("\nSetup full bunkbot config? (this file can be manually updated later) [Y/n]: " + OKWHITE)

    if create_config(do_setup):
        print_success("\nSetup complete. Run {0} to start the bot!".format(OKWHITE + "python3 main.py" + OKGREEN), True)
