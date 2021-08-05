"""Base object to be derived from with save/load/eq functionalities"""


class BaseObj:
    def __init__(self):
        pass

    def __to_json__(self):
        return {
            i: getattr(self, i)
            for i in dir(self)
            if not i.startswith("_") and not callable(getattr(self, i))
        }

    @classmethod
    def __from_dict__(cls, d):
        return cls(**d)

    def __eq__(self, other):
        return (
            isinstance(other, type(self)) and self.__to_json__() == other.__to_json__()
        )
