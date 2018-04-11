"""
Commands only allowable by admin, moderator, and vip
"""
from discord import PermissionOverwrite, ChannelPermissions, Server
from discord.ext import commands
from discord.ext.commands import command
from src.bunkbot import BunkBot
from src.util.constants import ROLE_ADMIN, ROLE_MODERATOR, ROLE_VIP
from src.storage.db import database


class Vip:
    def __init__(self, bot: BunkBot):
        self.bot = bot


    # if a user has enough level, allow
    # them to create their own channel
    @commands.has_any_role(ROLE_ADMIN, ROLE_MODERATOR)
    @command(pass_context=True, cls=None, help="Create a channel")
    async def channel(self, ctx) -> None:
        try:

            bunk_user = self.bot.get_user_by_id(ctx.message.author.id)

            if bunk_user is not None:
                # todo check channel from db

                cmds = self.bot.get_cmd_params(ctx)

                if len(cmds) == 0:
                    await self.bot.say("Please provide a channel name")
                    return

                ch_name = " ".join(cmds)
                ch_role = "_".join(cmds).lower()

                # first create the role responsible
                # for this new channel - i.e. the admin of the channel
                admin_role = await self.bot.create_role(self.bot.server, name="chadmin-{0}".format(ch_role))
                await self.bot.move_role(self.bot.server, admin_role, self.bot.lowest_role_position)

                #server: Server = self.bot.server
                #everyone_perms: PermissionOverwrite = PermissionOverwrite(read_messages=False)
                #my_perms: PermissionOverwrite = PermissionOverwrite(read_messages=True)

                #everyone = (server.default_role, everyone_perms)
                #new_ch = (server.)

                #await self.bot.create_channel(server, ch_name, everyone, mine)

        except Exception as e:
            await self.bot.handle_error(e, "create_channel")


def setup(bot: BunkBot):
    bot.add_cog(Vip(bot))