"""
Commands only allowable by admin and moderator
"""
from discord.ext import commands
from discord.ext.commands import command, Context
from src.bunkbot import BunkBot


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


def setup(bot: BunkBot):
    bot.add_cog(Mod(bot))