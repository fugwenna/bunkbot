from discord import Server

"""
Base class which all services should extend - this will
hold base information for BunkBot - server ref, database ref, etc
"""
class Service:
    def __init__(self):
        self.database = None
        self.server: Server = None


    # When bunkbot is loaded, all services
    # will load the server instance and other
    # default utils
    async def load(self, server: Server) -> None:
        self.server = server