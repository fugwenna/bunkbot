"""
Service solely designed to log errors directly to
an error log text file - rare case
"""
class ErrorLogService:
    # Log an error to the text file
    def log_error(self, message: str) -> None:
        print(message)

        with open("./storage/log.txt", "a+") as f:
            f.write(message)
