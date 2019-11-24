from discord import Member
from src.bunkbot import bunkbot
from src.services.registry import initialize

"""
Primary entry file for the discord bot which
initializes the one and only BunkBot

@author Kevin Yanuk
@license MIT
"""

@bunkbot.event
async def on_ready() -> None:
    await bunkbot.load()

@bunkbot.event
async def on_member_update(old: Member, new: Member) -> None:
    await bunkbot.handle_member_update(old, new)

if __name__ == "__main__":
    initialize(bunkbot)