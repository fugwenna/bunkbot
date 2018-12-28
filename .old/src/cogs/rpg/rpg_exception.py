from src.util.bunk_exception import BunkException


"""
Wrapper for an exception to be thrown
for cleaner bad command code
"""
class RPGException(BunkException):
    def __init__(self, message: str):
        super().__init__(message)