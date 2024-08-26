from zenlite.core.globs import pg, glm, np

class zenresource:
    def __init__(self, id:int) -> None:
        self.id=id

class zenbank:
    def __init__(self, max:int, *args, **kwargs):
        self.max:int=max
        self.count:int=0
