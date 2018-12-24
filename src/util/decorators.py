from discord.ext.commands import Context
from src.util.bunk_exception import BunkException

class BunkCommandArgument:
    def __init__(self, value: str, flag: str or None = None):
        self.value = value
        self.flag = flag

# decorator which will throw an error if
# an argument to a discord command is not given
# i.e. - "!yt" instead of "!yt some video"
def bunk_arguments(**kwargs):
    def decorator(fn):
        async def wrapper(self_arg, ctx: Context):
            if ctx is None:
                raise BunkException("No command context was passed")

            command_args = ctx.message.content.split()[1:]
            if kwargs["required"] and len(command_args) == 0:
                err_msg = kwargs["error_message"]
                if err_msg is None:
                    err_msg = "Please provide a command argument"

                raise BunkException(err_msg)

            return await fn(self_arg, ctx, command_args)
        return wrapper
    return decorator