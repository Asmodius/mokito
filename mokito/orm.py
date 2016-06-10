# coding: utf-8

import re
import six
from UserList import UserList

from bson import ObjectId
from tornado.gen import coroutine, Return

from errors import MokitoORMError
from client import Client
from ruler import Node

DEFAULT_URI = "mongodb://127.0.0.1:27017"


class Database(object):
    all_clients = {}

    @classmethod
    def get(cls, db_name):
        return cls.all_clients.get(db_name)

    @classmethod
    def set(cls, db_name, uri, *args, **kwargs):
        cls.all_clients[db_name] = Client(db_name, uri, *args, **kwargs)

    @classmethod
    def add(cls, db_name, uri, *args, **kwargs):
        if db_name not in cls.all_clients:
            cls.set(db_name, uri, *args, **kwargs)


class Documents(UserList):

    def __repr__(self):
        return '<%s: [%s]>' % (self.__class__.__name__, ', '.join(map(str, self.data)))

    def dirty_clear(self):
        for i in self.data:
            i.dirty_clear()

    def to_json(self, role=None, no_id=False):
        result = []
        for i in self.data:
            result.append(i.to_json(role, no_id))
        return result


class DocumentMeta(type):

    def __new__(cls, name, bases, attr):
        for i in ['__uri__', '__database__', 'fields', 'roles']:
            if i not in attr:
                for j in bases:
                    if hasattr(j, i):
                        attr[i] = getattr(j, i)
                        break

        if not attr.get('__collection__'):
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            attr['__collection__'] = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

        attr['fields'].setdefault('_id', ObjectId)
        attr['_ruler'] = Node.make(attr['fields'])
        if attr['__database__']:
            Database.add(attr['__database__'], attr['__uri__'] or DEFAULT_URI)
        return type.__new__(cls, name, bases, attr)


@six.add_metaclass(DocumentMeta)
class Document(object):
    __uri__ = DEFAULT_URI
    __database__ = None
    __collection__ = None
    fields = {}
    roles = {}

    @property
    def _id(self):
        return self._data['_id'].value()

    @property
    def pk(self):
        return self._data['_id'].value()

    @property
    def dirty(self):
        return self._data.dirty

    def __init__(self, *args, **kwargs):
        self._data = self._ruler()
        data = {}
        for i in args:
            data.update(i)
        data.update(kwargs)
        self._data.set(data)

    def __setitem__(self, name, val):
        self._data[name] = val

    def __getitem__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return self._data[name]

    def __unicode__(self):
        return '%s(%s)' % (self.__class__.__name__, self._data['_id'])

    def __str__(self):
        return str(self.__unicode__())

    @classmethod
    def _cursor(cls):
        try:
            return Database.get(cls.__database__)[cls.__collection__]
        except KeyError:
            raise MokitoORMError('Connection to the database "%s" not found' % cls.__database__)

    def dirty_clear(self):
        self._data.changed_clear()

    @classmethod
    @coroutine
    def find_one(cls, spec_or_id=None):
        cur = cls._cursor()
        data = yield cur.find_one(spec_or_id, fields=cls.fields.keys())
        if data:
            self = cls(data)
            self.dirty_clear()
            raise Return(self)

    @classmethod
    @coroutine
    def find(cls, spec=None, skip=0, limit=0, sort=None, hint=None):
        cur = cls._cursor()
        data = yield cur.find(spec, cls.fields.keys(), skip, limit, sort=sort, hint=hint)
        res = Documents(cls(i) for i in data)
        res.dirty_clear()
        raise Return(res)

    @classmethod
    @coroutine
    def count(cls, spec=None):
        cur = cls._cursor()
        data = yield cur.count(spec)
        raise Return(data)

    @coroutine
    def save(self):
        self._data.setdefault('_id', ObjectId())
        if self._data.dirty:
            cur = self._cursor()
            yield cur.update({"_id": self._data['_id'].value()}, self._data.query(), upsert=True)
            self.dirty_clear()

    def validate(self):
        pass

    def to_json(self, role=None, no_id=False):
        fields = set(self.roles[role] if role else self.fields.keys())
        if '_id' in fields:
            fields.remove('_id')

        data = {}
        _fields = set()
        for i in fields:
            if hasattr(self, i):
                data[i] = getattr(self, i)
            else:
                _fields.add(i)
        data.update(self._data.value(_fields))

        if not no_id:
            data['_id'] = str(self._data['_id'])

        return data

    @classmethod
    @coroutine
    def from_json(cls, *args, **kwargs):
        self = None
        data = {}
        for i in args:
            if isinstance(i, dict):
                data.update(i)
        data.update(kwargs)

        _id = data.pop('_id', None)
        if _id:
            self = yield cls.find_one(_id)
        if not self:
            self = cls()

        for k, v in data.items():
            try:
                self._data[k] = v
            except KeyError:
                pass
        raise Return(self)
