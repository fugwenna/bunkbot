from discord.ext import commands
from .util.cog_wheel import CogWheel
import json, discord

class ModCommands(CogWheel):
    def __init__(self, bot, token):
        CogWheel.__init__(self, bot)
        self.token = token

    """
    Double check server object reference"
    """
    def check_server(self):
        if self.server is None:
            self.server = self.bot.get_server(self.token)
            self.bot_testing = [ch for ch in self.server.channels if ch.name == "bot-testing"][0]
            self.mod_chat = [ch for ch in self.server.channels if ch.name == "mod-chat"][0]

    async def valid_channel(self, ctx):
        self.check_server()
        try:
            bad_channel = ["bot-testing", "mod-chat"].index(ctx.message.channel.name)
            return True
        except Exception as e:
            await self.bot.delete_message(ctx.message)
            await self.send_message_to_channel(self.mod_chat, "{0.mention} - Moderator commands only useable within this channel".format(ctx.message.author))
            return False

    """
    Get user info
    """
    @commands.has_any_role("admin", "moderator")
    @commands.command(pass_context=True, cls=None, help="Retrieve user information")
    async def user(self, ctx):
        try:
            if await self.valid_channel(ctx) == False:
                return

            await self.bot.send_typing(ctx.message.channel)

            params = self.get_cmd_params(ctx)

            if len(params) == 0:
                await self.send_message_plain("Enter a user name")
                return

            user_name = params[0].lower()
            users = [u for u in self.server.members if u.name.lower() == user_name]

            if len(users) == 0:
                await self.send_message_plain("Cannot locate user '" + user_name + "'")
                return

            #dat formatting
            user = users[0]
            info = "Display Name:  {}".format(user.display_name)
            info += "\nNick:                    {}".format(user.nick)
            info += "\nJoined:                {}".format(user.joined_at.strftime("%m/%d/%Y"))
            info += "\nTop Role:            {}".format(user.top_role)
            info += "\nRoles:                  {}".format(", ".join([r.name for r in user.roles if r.name != "@everyone"]))

            un_title = "User: {}".format(user.name)

            if len([r for r in user.roles if r.name == "new"]) > 0:
                un_title += " (new user)"

            await self.send_message(un_title, info, user.avatar_url)
        except Exception as e:
            await self.handle_error(e, "user")


def setup(bot):
    with open("config.json", "r") as config:
        conf = json.load(config)
        bot.add_cog(ModCommands(bot, conf["serverid"]))
