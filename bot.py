from os import walk
from discord.ext import commands
import json
bot = commands.Bot(command_prefix="!", description="The bunkest bot")

"""
Simple root event handler
that will process each cog command
"""
@bot.event
async def on_message(message):
    if message.author.bot:
        return

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

        for (path, names, files) in walk("cogs"):
            for f in files:
                fn = f.split(".")
                if fn[(len(fn)-1)] == "py":
                    try:
                        conf["cogs"].index(fn[0])
                        bot.load_extension(fn[0])
                    except:
                        pass

                    cog_arr.append(fn[0])

        config_data["token"] = conf["token"]
        config_data["cogs"] = cog_arr

    with open("config.json", "w") as config:
        json.dump(config_data, config, indent=4)

    bot.run(config_data["token"])
