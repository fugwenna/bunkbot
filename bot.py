import discord
import asyncio
import json

client = discord.Client()

@client.event
async def on_member_join(member):
    await client.send_message(message.channel, "Welcome to the Bunk Butter discord 0! Type '!help' for my available commands".format(member.nick))

@client.event
async def on_message(message):
    if message.content.startswith("!help"):
        await client.send_message(message.channel, "This is a test bot, no fun commands yet")

def load_credentials():
    with open("credentials.json") as creds:
        return json.load(creds)


if __name__ == "__main__":
    credentials = load_credentials();
    client.run(credentials["token"])
