"""
Wrapper for an exception to be thrown
for cleaner bad command code
"""
class BunkException(Exception):
    def __init__(self, message: str):
        super().__init__(self)
        self.raw_message: str = message
        self.message: str = ":exclamation: {0} :exclamation:".format(message)