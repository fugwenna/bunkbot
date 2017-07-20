"""
Primary entry file for the discord bot which initializes
the BunkBot class (collecting local cogs) and establishes
the static database instance for all cogs to use

@author Kevin Yanuk
@license MIT
"""
import discord
from src.bunkbot import bunkbot
from src.storage.db import database


@bunkbot.event
async def on_message(message: discord.Message) -> None:
    await bunkbot.process_message(message)


@bunkbot.event
async def on_member_join(member: discord.Member) -> None:
    await bunkbot.member_join(member)


@bunkbot.event
async def on_member_update(before: discord.Member, after: discord.Member) -> None:
    await bunkbot.member_update(before, after)


@bunkbot.event
async def on_ready() -> None:
    await bunkbot.on_init()


if __name__ == "__main__":
    bunkbot.run(database.get("token"))