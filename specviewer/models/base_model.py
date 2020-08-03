

class Base():
    def __init__(self):
        pass

    def from_dict(self, dict):
        for attr in self.__dict__:
            self.__dict__[attr] = dict[attr]

    def to_dict(self):
        return self.__dict__

    def to_string(self):
        return str(self.to_dict())

    def get_attributes(self):
        return [t for t in self.__dict__]
