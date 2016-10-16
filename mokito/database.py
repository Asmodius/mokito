# coding: utf-8

from client import Client


class Database(object):
    all_clients = {}

    def __int__(self):
        raise NotImplemented

    @classmethod
    def get(cls, db_name):
        return cls.all_clients.get(db_name)

    @classmethod
    def set(cls, db_name, uri, connect_count):
        cls.all_clients[db_name] = Client(db_name, uri, connect_count)

    @classmethod
    def add(cls, db_name, uri, connect_count):
        if db_name not in cls.all_clients:
            cls.set(db_name, uri, connect_count)

    @classmethod
    def close_all(cls):
        for i in cls.all_clients.values():
            i.close()
