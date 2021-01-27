class EventHook(object):
    """
    Basic "event system" from:
    http://www.voidspace.org.uk/python/weblog/arch_d7_2007_02_03.shtml#e616
    """
    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    async def emit(self, *args, **keywargs):
        for handler in self.__handlers:
            await handler(*args, **keywargs)