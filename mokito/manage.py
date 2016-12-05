# coding: utf-8

from client import Client


class ManagerMeta(type):
    def __contains__(cls, key):
        return (key in cls.data) or (key in cls.data.values())

    def __getitem__(self, key):
        return self.data[key]


class ModelManager(object):
    __metaclass__ = ManagerMeta
    data = {}

    @classmethod
    def add(cls, _class):
        from model import Field, Model
        cls.data[_class.__name__] = _class

        for _class in cls.data.values():
            if issubclass(_class, Model) and not getattr(_class, '_f', None):
                _class._f = Field.make(getattr(_class, 'fields', None))


class DBManager(object):
    __metaclass__ = ManagerMeta
    data = {}

    @classmethod
    def add(cls, _class):
        db_name = getattr(_class, '__database__', None)
        if db_name and db_name not in cls.data:
            cls.data[db_name] = Client(db_name,
                                       getattr(_class, '__uri__', None),
                                       getattr(_class, '__connect_count__', None))

    @classmethod
    def close_db(cls):
        for i in cls.data.values():
            i.close()
