# coding: utf-8

from client import Client


class ModelManager(object):
    models = {}
    databases = {}

    @classmethod
    def add(cls, _class):
        cls.models[_class.__name__] = _class

        db_name = getattr(_class, '__database__', None)
        if db_name and db_name not in cls.databases:
            cls.databases[db_name] = Client(db_name,
                                            getattr(_class, '__uri__', None),
                                            getattr(_class, '__connect_count__', None))

    @classmethod
    def close_db(cls):
        for i in cls.databases.values():
            i.close()
        # cls.databases = {}

