from .log_types import LOG_INFO, LOG_WARNING, LOG_ERROR
from ..core.constants import WARNING, ERROR, OKWHITE
from ..core.dates import get_now


class LogService:
    """
    Service solely designed to log errors directly to
    an error log text file - rare case
    """

    @staticmethod
    def format_message(txt: str, context: str, msg_type: str) -> None:
        """
        Format a message in a predefined format

        Parameters
        -----------
        txt: str
            Text of the message itself

        context: str
            'Context' of where the message originated

        msg_type: str
            Info, warning or error
        """
        return "{2} {0}: {1}".format(context, txt, msg_type)


    def log_info(self, message: str, context: str, do_print: bool = True) -> None:
        """
        Log information to a log file or console

        Parameters
        -----------
        message: str
            Message to sendo
        
        context: str
            Context or origination of the message

        do_print: bool (default True)
            Print the message to the console 
        """
        self._log(message, context, LOG_INFO, do_print)


    def log_warning(self, message: str, context: str, do_print: bool = True) -> None:
        """
        Log a warning to a log file or console

        Parameters
        -----------
        message: str
            Message to sendo
        
        context: str
            Context or origination of the message

        do_print: bool (default True)
            Print the message to the console 
        """
        self._log(message, context, LOG_WARNING, do_print)


    def log_error(self, message: str, context: str, do_print: bool = True) -> None:
        """
        Log an error to a log file or console

        Parameters
        -----------
        message: str
            Message to sendo
        
        context: str
            Context or origination of the message

        do_print: bool (default True)
            Print the message to the console 
        """
        self._log(message, context, LOG_ERROR, do_print)


    def _log(self, message: str, context: str, msg_type: str, do_print: bool = True) -> None:
        # Log an error to the text file
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
