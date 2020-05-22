from config import create_config
from ezio import print_success


"""
This is the primary setup file for the bot. This is to be ran once after the user 
first clones the project so that the specific channels/roles/constants can be defined
within a config.json file (this is not the same as db.json)
"""

if __name__ == "__main__":
    if create_config():
        print_success("Setup complete.", True)
