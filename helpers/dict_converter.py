class Dict2Obj(object):
    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def __repr__(self):
        attr = str([x for x in self.__dict__])
        return "<Dict2Obj: %s>" % attr
