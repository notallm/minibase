class Dummy(object):
    pass

class DotDict():
    def __init__(self, parent: dict) -> None:
        for key, value in parent.items():
            setattr(Dummy, key, value)

    def __getattr__(self, key: object) -> object:
        return {key: getattr(Dummy, key)}
