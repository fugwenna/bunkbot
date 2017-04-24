from discord.ext import commands
from cogs.util.chatbot import Chatbot
import json, re, os, os.path

cbot_token = ""
bot = commands.Bot(command_prefix="!", description="The bunkest bot - say my name to chat with me\n My source code: https://github.com/fugwenna/bunkbot")
chatbot = {}

"""
Simple root event handler
that will process each cog command
"""
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    try:
        if str(message.content) == "!reset":
            global chatbot
            chatbot = Chatbot(bot, cbot_token)
        else:
            if chatbot.is_chatting or chatbot.is_mention(message):
                await chatbot.reply(message)
            else:
                await bot.process_commands(message)
    except Exception as ex:
        print(ex)
        pass

"""
Greet new users
"""
@bot.event
async def on_member_join(member):
    server = member.server
    fmt = "Welcome {0.mention} to {1.name}!  Type !help for a list of my commands"
    await bot.send_message(server, fmt.format(member, server))

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

        config_data["cleverbot"] = conf["cleverbot"]
        config_data["weather"] = conf["weather"]
        config_data["token"] = conf["token"]
        config_data["serverid"] = conf["serverid"]
        config_data["cogs"] = cog_arr

        cbot_token = config_data["cleverbot"]
        chatbot = Chatbot(bot, cbot_token)

    with open("config.json", "w") as config:
        json.dump(config_data, config, indent=4)

    bot.run(config_data["token"])
