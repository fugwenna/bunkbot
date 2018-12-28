"""
Primary entry file for the discord bot which
initializes the one and only BunkBot

@author Kevin Yanuk
@license MIT
"""
from .src.bunkbot import bunkbot


if __name__ == "__main__":
    bunkbot.run()#database.get("token"))