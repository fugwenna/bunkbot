"""
Wrapper for an exception to be thrown
for cleaner bad command code
"""
class BunkException(Exception):
    def __init__(self, message: str):
        super().__init__(self)
        self.message = ":exclamation: {0} :exclamation:".format(message)