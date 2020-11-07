class BunkException(Exception):
    """
    Wrapper for an exception to be thrown
    for cleaner bad command code

    Parameters
    -----------
    message: str
        Descripton of the error itself
    """
    def __init__(self, message: str):
        super().__init__(self)
        self.raw_message: str = message
        self.message: str = ":exclamation: {0} :exclamation:".format(message)