import json
import asyncio
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", description="The bunkest bot")

exts = [
    "cogs.remindme"
]

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

def load_credentials():
    with open("credentials.json") as creds:
        return json.load(creds)

if __name__ == "__main__":
    credentials = load_credentials();

    for ext in exts:
        bot.load_extension(ext)

    bot.run(credentials["token"])
