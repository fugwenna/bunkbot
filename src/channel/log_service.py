from .log_types import LOG_INFO, LOG_WARNING, LOG_ERROR
from ..core.constants import WARNING, ERROR, OKWHITE
from ..core.dates import get_now


"""
Service solely designed to log errors directly to
an error log text file - rare case
"""
class LogService:
    def log_info(self, message: str, context: str, do_print: bool = True) -> None:
        self._log(message, context, LOG_INFO, do_print)

    def log_warning(self, message: str, context: str, do_print: bool = True) -> None:
        self._log(message, context, LOG_WARNING, do_print)

    def log_error(self, message: str, context: str, do_print: bool = True) -> None:
        self._log(message, context, LOG_ERROR, do_print)

    # Log an error to the text file
    def _log(self, message: str, context: str, msg_type: str, do_print: bool = True) -> None:
        message = self.format_message(message, context, msg_type)

        if (do_print):
            if msg_type == LOG_WARNING:
                print(WARNING + message)
            elif msg_type == LOG_ERROR:
                print(ERROR + message)
            else:
                print(OKWHITE + message)

        with open("./src/db/log.txt", "a+") as f:
            f.write("{0}\n".format(get_now()))
            f.write("{0}\n\n".format(message))


    @staticmethod
    def format_message(txt: str, context: str, msg_type: str) -> None:
        return "{2} {0}: {1}".format(context, txt, msg_type)
