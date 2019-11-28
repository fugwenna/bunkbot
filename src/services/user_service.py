from typing import List
from discord import Member

from .channel_service import ChannelService
from .database_service import DatabaseService
from .role_service import RoleService
from ..bunkbot import BunkBot
from ..models.service import Service
from ..models.bunk_user import BunkUser
from ..models.event_hook import EventHook
from ..util.constants import ROLE_GAMING, ROLE_STREAMING, ROLE_MODERATOR, ROLE_VIP

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
        self.bot.on_user_update += self.handle_user_update
        self.on_user_gaming: EventHook = EventHook()


    # when the main bot is loaded, collect
    # members from the server and initialize
    # bunkuser instances for future use
    async def load(self) -> None:
        await super().load()

        new_users: List[str] = []

        for member in self.server.members:
            # check the database if this user
            # has been added before collecting
            # a new instance of a bunk user
            db_user = self.database.get_user_by_member_ref(member)

            # ignore bot users
            if db_user is not None:
                user: BunkUser = BunkUser(member, db_user)
                self.users.append(user)
                await self.update_current_member_state(user, user, True)

                if db_user.was_added:
                    new_users.append(user.full_name)

        if len(new_users) > 0:
            new_user_msg = "New users: {0}".format(", ".join(new_users)) 
            await self.channels.log_info(new_user_msg, self.channels.NEW_USER_LOG)


    # retrieve a user based on the member
    # identifier
    def get_by_id(self, mid: int) -> BunkUser:
        return next(u for u in self.users if u.id == mid)


    # send out various events to other services when
    # a user has been updated in some way
    async def handle_user_update(self, old_ref: Member, member: Member, force: bool = False) -> None:
        # create a fake user to check the is_gaming status
        old_usr: BunkUser = BunkUser(old_ref, None)
        user: BunkUser = self.get_by_id(member.id)
        await self.update_current_member_state(old_usr, user, force)

    
    # resuable function for updating states
    async def update_current_member_state(self, old_usr: BunkUser, user: BunkUser, force: bool = False) -> None:
        await self.check_user_gaming(old_usr, user, force)
        await self.check_user_streaming(old_usr, user, force)


    # check if the user is/was gaming and update their 
    # role accordingly
    async def check_user_gaming(self, old_usr: BunkUser, user: BunkUser, force: bool = False) -> None:
        is_gaming = False
        was_gaming = False

        if force:
            is_gaming = user.is_gaming
        else:
            was_gaming = old_usr.is_gaming and not user.is_gaming
            is_gaming = not old_usr.is_gaming and user.is_gaming

        if is_gaming:
            await self.on_user_gaming.emit(user)
            await self.roles.add_role(user, ROLE_GAMING)
        elif was_gaming:
            await self.roles.rm_role(user, ROLE_GAMING)


    # check if the user is/was streaming and update their 
    # role accordingly
    async def check_user_streaming(self, old_usr: BunkUser, user: BunkUser, force: bool = False) -> None:
        is_streaming = False
        was_streaming = False

        if force:
            is_streaming = user.is_streaming
        else:
            was_streaming = old_usr.is_streaming and not user.is_streaming
            is_streaming = not old_usr.is_streaming and user.is_streaming

        if is_streaming:
            await self.roles.add_role(user, ROLE_STREAMING)
            await self.update_elevated_user_roles(user, True)
        elif was_streaming:
            await self.roles.rm_role(user, ROLE_STREAMING)
            await self.update_elevated_user_roles(user, False)


    # when coming back from something like streaming, make sure
    # aesthetic roles are reapplied
    async def update_elevated_user_roles(self, user: BunkUser, rm: bool) -> None:
        if user.is_moderator:
            if rm:
                self.roles.rm_role(user, ROLE_MODERATOR)
            else:
                self.roles.add_role(user, ROLE_MODERATOR)

        if user.is_vip:
            if rm:
                self.roles.rm_role(user, ROLE_VIP)
            else:
                self.roles.add_role(user, ROLE_VIP)
