from discord.ext import commands
from cogs.util.chatbot import Chatbot
import json, re, os, os.path

bot = commands.Bot(command_prefix="!", description="The bunkest bot")
chatbot = Chatbot(bot)

"""
Simple root event handler
that will process each cog command
"""
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if str(message.content) == "!reset":
        global chatbot
        chatbot = Chatbot(bot)
    else:
        if chatbot.is_chatting or chatbot.is_mention(message):
            await chatbot.reply(message)
        else:
            await bot.process_commands(message)

"""
Main loader - read over cogs/ directory
and manually update the cogs array in 
the config.json file
"""
if __name__ == "__main__":
    cog_arr = []
    config_data = {}

    with open("config.json", "r") as config:
        conf = json.load(config)
        for f in [f for f in os.listdir("cogs") if os.path.isfile(os.path.join("cogs", f))]:
            fn = "cogs.{0}".format(f.split(".")[0])
            bot.load_extension(fn)
            cog_arr.append(fn)

        config_data["token"] = conf["token"]
        config_data["cogs"] = cog_arr

    with open("config.json", "w") as config:
        json.dump(config_data, config, indent=4)

    bot.run(config_data["token"])
