"""
Commands only allowable by admin and moderator
"""
from discord.ext import commands
from discord.ext.commands import command, Context
from src.bunkbot import BunkBot
from src.util.bunk_user import BunkUser
from src.util.bunk_exception import BunkException

class Mod:
    def __init__(self, bot: BunkBot):
        self.bot: BunkBot = bot


    # unlock the server and do not allow invitations
    @commands.has_any_role("admin", "moderator")
    @command(pass_context=True, cls=None, help="Lock the server")
    async def lock(self, ctx: Context) -> None:
        if self.bot.SERVER_LOCKED:
            await self.bot.say_to_channel(self.bot.mod_chat, "Server is already locked")
            return

        self.bot.SERVER_LOCKED = True
        await self.bot.say_to_channel(self.bot.mod_chat, ":shield: SERVER LOCKED :shield: Invited members will be automatically kicked")

        if ctx.message.channel != self.bot.mod_chat:
            await self.bot.delete_message(ctx.message)


    # unlock the server and allow invitations
    @commands.has_any_role("admin", "moderator")
    @command(pass_context=True, cls=None, help="Unlock the server")
    async def unlock(self, ctx: Context) -> None:
        if not self.bot.SERVER_LOCKED:
            await self.bot.say_to_channel(self.bot.mod_chat, "Server is not locked")
            return

        self.bot.SERVER_LOCKED = False
        await self.bot.say_to_channel(self.bot.mod_chat, "SERVER UNLOCKED: Invitations allowed")

        if ctx.message.channel != self.bot.mod_chat:
            await self.bot.delete_message(ctx.message)


    # last_online
    @commands.has_any_role("admin", "moderator")
    @command(pass_context=True, cls=None, help="Find the last online of a user", aliases=["last", "online", "lo"])
    async def lastonline(self, ctx: Context) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            if ctx.message.channel != self.bot.mod_chat:
                await self.bot.delete_message(ctx.message)

            cmds = self.bot.get_cmd_params(ctx)
            if len(cmds) == 0:
                await self.bot.say("Please enter a user name")
                return

            user: BunkUser = self.bot.get_user(" ".join(cmds[0:]))

            await self.bot.say_to_channel(self.bot.mod_chat, "User {0} last online {1}".format(user.name, user.last_online))

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "lastonline")

    # last_xp
    @commands.has_any_role("admin", "moderator")
    @command(pass_context=True, cls=None, help="Find the last online of a user", aliases=["last", "lastxp", "lxp", "active", "lastactive"])
    async def lastxpupdate(self, ctx: Context) -> None:
        try:
            await self.bot.send_typing(ctx.message.channel)

            if ctx.message.channel != self.bot.mod_chat:
                await self.bot.delete_message(ctx.message)

            cmds = self.bot.get_cmd_params(ctx)
            if len(cmds) == 0:
                await self.bot.say("Please enter a user name")
                return

            user: BunkUser = self.bot.get_user(" ".join(cmds[0:]))

            await self.bot.say_to_channel(self.bot.mod_chat, "User {0} last last active {1}".format(user.name, user.last_xp_updated))

        except BunkException as be:
            await self.bot.say(be.message)
        except Exception as e:
            await self.bot.handle_error(e, "lastxpupdate")

def setup(bot: BunkBot):
    bot.add_cog(Mod(bot))