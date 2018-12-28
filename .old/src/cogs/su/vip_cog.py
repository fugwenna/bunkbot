"""
Commands only allowable by admin, moderator, and vip
"""
from discord import PermissionOverwrite, ChannelPermissions, Server, ChannelType
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
    @commands.has_any_role(ROLE_ADMIN)
    @command(pass_context=True, cls=None, help="Create a channel")
    async def channel(self, ctx) -> None:
        admin_role = None
        ch_category = None

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
                role_name = "chadmin-{0}".format(ch_role)

                existing = await self.bot.get_role(role_name)
                if existing is not None:
                    await self.bot.say("Role '{0}' for channel '{1}' already exists".format(role_name, ch_name))
                    return

                # first create the role responsible
                # for this new channel - i.e. the admin of the channel
                admin_role = await self.bot.create_role(self.bot.server, name=role_name)
                await self.bot.move_role(self.bot.server, admin_role, self.bot.lowest_role_position)

                await self.bot.add_roles(ctx.message.author, admin_role)

                server: Server = self.bot.server
                everyone_perms: PermissionOverwrite = PermissionOverwrite(read_messages=False)
                admin_perms: PermissionOverwrite = PermissionOverwrite(
                    read_messages=True, send_messages=True, manage_channel=True, manage_messages=True)

                everyone = (server.default_role, everyone_perms)
                mine = (admin_role, admin_perms)
                bbot = (self.bot.role_bunky, admin_perms)

                ch_category = await self.bot.create_channel(server, ch_name, everyone, mine, bbot, type=4)
                await self.bot.say_to_channel(ch_category, "{0} category/channel created!".format(ctx.message.author.mention))
                await self.bot.create_channel(ch_category, "General", everyone, mine, bbot)

        except Exception as e:
            try:
                if admin_role is not None:
                    await self.bot.remove_roles(ctx.message.author, admin_role)
                    await self.bot.delete_role(admin_role)

                if ch_category is not None:
                    await self.bot.delete_channel(ch_category)

            except Exception as e2:
                await self.bot.handle_error(e2, "create_channel")

            await self.bot.handle_error(e, "create_channel")


def setup(bot: BunkBot):
    bot.add_cog(Vip(bot))