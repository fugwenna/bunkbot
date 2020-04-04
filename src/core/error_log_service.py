from .dates import get_now

"""
Service solely designed to log errors directly to
an error log text file - rare case
"""
class ErrorLogService:
    def log_warning(self, message: str, context: str, do_print: bool = True) -> None:
        self.log(message, context, "WARNING")

    def log_error(self, message: str, context: str, do_print: bool = True) -> None:
        self.log(message, context, "ERROR")

    # Log an error to the text file
    def log(self, message: str, context: str, msg_type: str, do_print: bool = True) -> None:
        message = self.format_message(message, context, msg_type)

        if (do_print):
            print(message)

        with open("./src/db/log.txt", "a+") as f:
            f.write("{0}\n".format(get_now()))
            f.write("{0}\n\n".format(message))


    @staticmethod
    def format_message(txt: str, context: str, msg_type: str) -> None:
        return "[{2}] {0}: {1}".format(context, txt, msg_type)