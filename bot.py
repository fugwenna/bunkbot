from discord.ext import commands
from cogs.util.chatbot import Chatbot
import json, re, os, os.path, datetime

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

    for role in server.roles:
        if role.name == "new":
            reset_config(False)
            await bot.add_roles(member, role)
            break

    await bot.send_message(server, fmt.format(member, server))

"""
Update the streamerz
"""
@bot.event
async def on_member_update(before, after):
    stream_role = [r for r in after.server.roles if r.name == "streaming"][0]
    member_streaming = [r for r in after.roles if r.name == "streaming"]

    if after.game is not None and after.game.type == 1:
        if len(member_streaming) == 0:
            await bot.add_roles(after, stream_role)

    elif before.game is not None and before.game.type == 1:
        if len(member_streaming) > 0:
            await bot.remove_roles(after, stream_role)

"""
Simple reusable function for
resetting server config
"""
def reset_config(add_cb=True):
    cog_arr = []
    config_data = {}

    with open("config.json", "r") as config:
        conf = json.load(config)
        for f in [f for f in os.listdir("cogs") if os.path.isfile(os.path.join("cogs", f))]:
            fn = "cogs.{0}".format(f.split(".")[0])
            bot.load_extension(fn)
            cog_arr.append(fn)

        cbot_token = conf["cleverbot"]

        if add_cb:
            global chatbot
            chatbot = Chatbot(bot, cbot_token)

        config_data["cleverbot"] = conf["cleverbot"]
        config_data["weather"] = conf["weather"]
        config_data["token"] = conf["token"]
        config_data["serverid"] = conf["serverid"]
        config_data["cogs"] = cog_arr

    with open("config.json", "w") as config:
        json.dump(config_data, config, indent=4)

    return config_data

"""
Main loader - read over cogs/ directory
and manually update the cogs array in 
the config.json file
"""
if __name__ == "__main__":
    config_data = reset_config()
    bot.run(config_data["token"])
