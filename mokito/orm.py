# coding: utf-8

import re
import six
import itertools
from UserList import UserList

from bson import ObjectId, DBRef
from tornado.gen import coroutine, Return
from tornado.concurrent import is_future

from errors import MokitoORMError
from ruler import Node, NodeDocument
from tools import KnownClasses, SEPARATOR
from database import Database

DEFAULT_URI = "mongodb://127.0.0.1:27017"


# TODO: добавить self.set(data)
# PS. все таки надо переписывать ruler.NodeDocument и Document
# PPS. и подумать на предмет отказаться от node.value()
# PPPS. но это уже в версии 0.2


class Documents(UserList):
    # TODO: а этот класс поменять на ruler.NodeArray

    def __repr__(self):
        return '<%s: [%s]>' % (self.__class__.__name__, ', '.join(map(str, self.data)))

    def dirty_clear(self):
        map(lambda i: i.dirty_clear(), self.data)

    @coroutine
    def preload(self, *fields, **kwargs):
        cache = kwargs.get('cache', {})
        yield [i.preload(*fields, cache=cache) for i in self.data]

    @coroutine
    def to_json(self, *role, **kwargs):
        cache = kwargs.get('cache', {})
        raise Return([(yield i.to_json(*role, cache=cache)) for i in self.data])


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
        _cls = type.__new__(cls, name, bases, attr)
        if attr['__database__']:
            Database.add(attr['__database__'], attr['__uri__'] or DEFAULT_URI)
            KnownClasses.add(_cls)
        return _cls


@six.add_metaclass(DocumentMeta)
class Document(object):
    __uri__ = DEFAULT_URI
    __database__ = None
    __collection__ = None
    fields = {}
    roles = {}

    def __init__(self, *args, **kwargs):
        self._data = self._ruler()
        data = {}
        for i in args:
            data.update(i)
        data.update(kwargs)
        if data:
            self._data.set(data)

    def __setitem__(self, name, val):
        self._data[name] = val

    def __getitem__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return self._data[name]

    def __delitem__(self, key):
        self._data.__delitem__(key)

    def __unicode__(self):
        return '%s(%s)' % (self.__class__.__name__, self._data['_id'])

    def __str__(self):
        return str(self.__unicode__())

    @property
    def pk(self):
        return self._data['_id'].value()

    @property
    def _id(self):
        return str(self._data['_id'].value())

    @property
    def dbref(self):
        return DBRef(self.__collection__, self.pk)

    @property
    def dirty(self):
        return self._data.dirty

    def dirty_clear(self):
        self._data.dirty_clear()

    def is_dirty(self, *keys):
        return self._data.is_dirty(*keys)

    def value(self, default=None):
        return self._data.value(default)

    @classmethod
    def _cursor(cls, database=None, collection=None):
        db = database or cls.__database__
        try:
            return Database.get(db)[collection or cls.__collection__]
        except KeyError:
            raise MokitoORMError('Connection to the database "%s" not found' % db)

    @coroutine
    def preload(self, *fields, **kwargs):
        node = kwargs.get('node', self._data)
        cache = kwargs.get('cache', {})

        fields = set(fields)
        fields.discard('')

        for i in fields:
            k1, _, k2 = str(i).partition(SEPARATOR)
            _node = node[k1]
            if isinstance(_node, NodeDocument):
                if not _node.been_set or _node.dirty:
                    dbref = _node.dbref
                    if dbref.id is not None:
                        data = cache.get(dbref)
                        if not data:
                            cur = self._cursor(dbref.database, dbref.collection)
                            data = yield cur.find_one(dbref.id, fields=_node.fields.keys())
                            cache[dbref] = data
                        _node.set(data)
                        _node.dirty_clear()
            else:
                yield self.preload(k2, node=_node, cache=cache)

    @classmethod
    @coroutine
    def find_one_raw(cls, spec_or_id, *fields):
        cur = cls._cursor()
        data = yield cur.find_one(spec_or_id, fields=fields)
        raise Return(data)

    @classmethod
    @coroutine
    def find_one(cls, spec_or_id, preload=False):
        cur = cls._cursor()
        fields = cls.fields.keys()
        data = yield cur.find_one(spec_or_id, fields=fields)
        if data:
            self = cls(data)
            self.dirty_clear()
            if preload:
                yield self.preload(*fields)
            raise Return(self)

    @classmethod
    @coroutine
    def find_raw(cls, spec=None, *fields):
        cur = cls._cursor()
        data = yield cur.find(spec, fields=fields)
        raise Return(data)

    @classmethod
    @coroutine
    def find(cls, spec=None, skip=0, limit=0, sort=None, hint=None, preload=False):
        cur = cls._cursor()
        fields = cls.fields.keys()
        data = yield cur.find(spec, fields, skip, limit, sort=sort, hint=hint)
        res = Documents(cls(i) for i in data)
        res.dirty_clear()
        if preload:
            yield res.preload(*fields)
        raise Return(res)

    @classmethod
    @coroutine
    def count(cls, spec=None):
        cur = cls._cursor()
        data = yield cur.count(spec)
        raise Return(data)

    @classmethod
    @coroutine
    def distinct(cls, key, spec=None):
        cur = cls._cursor()
        data = yield cur.distinct(key, spec)
        raise Return(data)

    @coroutine
    def save(self):
        self._data.setdefault('_id', ObjectId())
        if self._data.dirty:
            cur = self._cursor()
            yield cur.update({"_id": self._data['_id'].value()}, self._data.query, upsert=True)
            self.dirty_clear()

    @coroutine
    def remove(self, safe=False):
        cur = cls._cursor()
        yield cur.remove(self['_id'].value(), safe)
        self['_id'] = None

    @coroutine
    def to_json(self, *role, **kwargs):
        """
        converts the attributes into a dictionary
        :param role: Role name or list of role name. The role needs to be defined in the class
            attribute "roles". If the role is None then converted all the fields.
        :return: dict
        """
        fields = set(itertools.chain(*[self.roles[i] for i in role]) if role else self.fields.keys())
        data = {}
        _fields = set()
        for i in fields:
            if hasattr(self, i):
                v = getattr(self, i)
                if is_future(v):
                    v = yield v
                data[i] = v
            else:
                _fields.add(i)

        cache = kwargs.get('cache', {})
        yield self.preload(*[i for i in _fields if '.' in i], cache=cache)
        for i in _fields:
            try:
                v = self._data[i].value()
            except ValueError:
                v = None
            else:
                if isinstance(v, Document):
                    v = yield v.to_json()
            data[i] = v

        raise Return(data)

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
