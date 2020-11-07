from typing import List
from discord import Member

from .role_service import RoleService
from ..bunkbot import BunkBot
from ..channel.channel_service import ChannelService
from ..core.bunk_user import BunkUser
from ..core.constants import ROLE_GAMING, ROLE_SHOW_GAMING, ROLE_STREAMING, ROLE_MODERATOR, ROLE_VIP
from ..core.event_hook import EventHook
from ..core.service import Service
from ..db.database_service import DatabaseService
from ..db.database_user import DatabaseUser


"""
Service responsible for handling any
bunk user references + syncing with database
"""
class UserService(Service):
    def __init__(self, bot: BunkBot, database: DatabaseService, roles: RoleService, channels: ChannelService):
        super().__init__(bot, database)
        self.users: List[BunkUser] = []
        self.roles: RoleService = roles
        self.channels: ChannelService = channels
        self.bot.on_user_joined += self.add_new_user
        self.bot.on_user_update += self.handle_user_update
        self.bot.on_user_remove += self.handle_user_removal
        self.on_user_gaming: EventHook = EventHook()


    # when the main bot is loaded, collect
    # members from the server and initialize
    # bunkuser instances for future use
    async def load(self) -> None:
        await super().load()

        new_users: List[str] = []

        if self.server is None:
            self.channels.log_warning("Server could not be found, users cannot be loaded", "UserService")
        else:
            for member in self.server.members:
                # check the database if this user
                # has been added before collecting
                # a new instance of a bunk user
                db_user: DatabaseUser = self.database.get_user_by_member_ref(member)

                # ignore bot users
                if db_user is not None:
                    user: BunkUser = BunkUser(member, db_user)
                    self.users.append(user)
                    await self.update_current_member_state(user, user, True)

                    if db_user.was_added:
                        new_users.append(user.full_name)

                    if user.is_admin:
                        self.bot.ADMIN_USER = user

            if len(new_users) > 0:
                new_user_msg = "New users: {0}".format(", ".join(new_users)) 
                await self.channels.log_info(new_user_msg)

        await self.roles.prune_orphaned_roles("color-")

    
    # when a new user has joined the server, check
    # if they already exist in the database (left and came back)
    # and add them accordingly - send a message to the server welcoming
    # the new user
    async def add_new_user(self, member: Member) -> None:
        user: DatabaseUser = self.database.get_user_by_member_ref(member)
        bunk_user: BunkUser = BunkUser(member, user)
        welcome_msg: str = "Welcome {0}, to Bunk Butter!"

        self.users.append(bunk_user)

        if not user.was_added:
            welcome_msg = "Welcome back, {0}"

        await self.channels.send_to_primary_channel(welcome_msg.format(bunk_user.mention))
        await self.channels.log_info("{0} has joined the server {1}".format(bunk_user.name, self.bot.ADMIN_USER.mention))


    # inform moderators when users are removed from the server
    async def handle_user_removal(self, member: Member) -> None:
        await self.channels.log_info(":x: {0} has left the server {1}".format(member.name, self.bot.ADMIN_USER.mention))
        await self.roles.prune_orphaned_roles("color-")


    # retrieve a user based on the member
    # identifier
    def get_by_id(self, mid: int) -> BunkUser:
        try:
            return next((u for u in self.users if u.id == mid), None)
        except Exception as e:
            self.channels.log_error(e, "get_by_id")


    # retrieve a user by a "fuzzy" search 
    # on their username (basic)
    def get_by_username(self, un: str) -> None:
        try:
            return next((u for u in self.users if u.name == un), None)
        except Exception as e:
            self.channels.log_error(e, "get_by_username")


    # send out various events to other services when
    # a user has been updated in some way
    async def handle_user_update(self, old_ref: Member, member: Member, force: bool = False) -> None:
        # create a fake user to check the is_gaming status
        old_usr: BunkUser = BunkUser(old_ref, None)
        user: BunkUser = self.get_by_id(member.id)

        if old_usr is not None and user is not None:
            await self.update_current_member_state(old_usr, user, force)

        if self.roles is not None:
            await self.roles.prune_orphaned_roles("color-")

    
    # resuable function for updating states
    async def update_current_member_state(self, old_usr: BunkUser, user: BunkUser, force: bool = False) -> None:
        await self.check_user_gaming(old_usr, user, force)
        await self.check_user_streaming(old_usr, user, force)


    # check if the user is/was gaming and update their 
    # role accordingly
    async def check_user_gaming(self, old_usr: BunkUser, user: BunkUser, force: bool = False) -> None:
        is_gaming: bool = False
        was_gaming: bool = False

        if force:
            is_gaming = user.is_gaming
        else:
            was_gaming = old_usr.is_gaming and not user.is_gaming
            is_gaming = not old_usr.is_gaming and user.is_gaming

        if is_gaming:
            await self.on_user_gaming.emit(user)
            await self.roles.add_role(ROLE_GAMING, user)

            sg_role = self.roles.get_role_by_pattern("color-", user.member.roles)

            if sg_role is None:
               await self.roles.add_role(ROLE_SHOW_GAMING, user) 
        elif was_gaming:
            await self.roles.rm_role(ROLE_GAMING, user)

            if user.has_role(ROLE_SHOW_GAMING):
                await self.roles.rm_role(ROLE_SHOW_GAMING, user)


    # check if the user is/was streaming and update their 
    # role accordingly
    async def check_user_streaming(self, old_usr: BunkUser, user: BunkUser, force: bool = False) -> None:
        is_streaming: bool = False
        was_streaming: bool = False

        if force:
            is_streaming = user.is_streaming
        else:
            was_streaming = old_usr.is_streaming and not user.is_streaming
            is_streaming = not old_usr.is_streaming and user.is_streaming

        if is_streaming:
            await self.roles.add_role(ROLE_STREAMING, user)
            await self.update_elevated_user_roles(user, True)
            await self.channels.log_info(":tv: {0} is now streaming".format(user.name))
        elif was_streaming:
            await self.roles.rm_role(ROLE_STREAMING, user)
            await self.update_elevated_user_roles(user, False)


    # when coming back from something like streaming, make sure
    # aesthetic roles are reapplied
    async def update_elevated_user_roles(self, user: BunkUser, rm: bool) -> None:
        if user.is_moderator:
            if rm:
                await self.roles.rm_role(ROLE_MODERATOR, user)
            else:
                await self.roles.add_role(ROLE_MODERATOR, user)

        if user.is_vip:
            if rm:
                await self.roles.rm_role(ROLE_VIP, user)
            else:
                await self.roles.add_role(ROLE_VIP, user)
