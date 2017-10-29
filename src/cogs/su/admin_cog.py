"""
Commands only allowable by admin
"""
from discord.ext import commands
from discord.ext.commands import command
from src.bunkbot import BunkBot

class Admin:
    def __init__(self, bot: BunkBot):
        self.bot = bot


    # link bunkbot source code
    @commands.has_any_role("admin")
    @command(pass_context=True, cls=None, help="Link source code url", aliases=["src"])
    async def source(self, ctx) -> None:
        try:
            await self.bot.send_typing(ctx)
            await self.bot.send_message(ctx.message.channel, "https://github.com/fugwenna/bunkbot/")
        except Exception as e:
            await self.bot.handle_error(e, "source")


    # clear a role for ALL users ...
    # be careful with this, basically an rm -rf
    @commands.has_any_role("admin")
    @command(pass_context=True, cls=None, help="Clear a role from all users")
    async def clear(self, ctx) -> None:
        try:
            param = self.bot.get_cmd_params(ctx)[0]
            role = [r for r in self.bot.server.roles if r.name == param][0]

            await self.bot.send_message(self.bot.mod_chat, "Clearing {0}...".format(param))
            for m in self.bot.server.members:
                await self.bot.remove_roles(m, role)

            await self.bot.send_message(self.bot.mod_chat,
                                        "Role {0} cleared from all users... good job idiot".format(param))

        except Exception as e:
            await self.bot.handle_error(e, "clear")


def setup(bot: BunkBot):
    bot.add_cog(Admin(bot))