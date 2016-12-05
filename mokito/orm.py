# coding: utf-8

import re
import six
import itertools
from UserList import UserList

from bson import ObjectId, DBRef
from tornado.gen import coroutine, Return
from tornado.concurrent import is_future

from errors import MokitoORMError
from ruler import Node, NodeDocument, NodeComposite
from known_cls import KnownClasses
from tools import SEPARATOR
from database import Database

DEFAULT_URI = "mongodb://127.0.0.1:27017"
DEFAULT_CONNECTIONS = 10


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
    def reread(self, *fields):
        map(lambda i: (yield i.reread(*fields)), self.data)

    @coroutine
    def preload(self, *fields, **kwargs):
        cache = kwargs.get('cache', {})
        yield [i.preload(*fields, cache=cache) for i in self.data]

    @coroutine
    def remove(self, safe=True):
        if self.data:
            ids = [i.pk for i in self.data]
            cur = self.data[0].get_cursor()
            yield cur.remove({"_id": {"$in": ids}}, safe)
            for i in self.data:
                i['_id'] = None

    def filter(self, fn):
        return Documents(filter(fn, self.data))

    @coroutine
    def to_json(self, *roles, **kwargs):
        data = []
        if self.data:
            field_data = self.data[0].fields_to_data(*roles)
            cache = kwargs.get('cache', {})
            data = [(yield i.to_json_raw(field_data, cache=cache)) for i in self.data]
        raise Return(data)


class DocumentMeta(type):

    def __new__(mcs, name, bases, attr):
        for i in ['__uri__', '__database__', '__connect_count__',
                  'fields', 'roles', 'aliases']:
            if i not in attr:
                for j in bases:
                    if hasattr(j, i):
                        attr[i] = getattr(j, i)
                        break

        for i in bases:
            if hasattr(i, 'fields'):
                x = i.fields.copy()
                x.update(attr['fields'])
                attr['fields'] = x
            if hasattr(i, '__collection__'):
                attr.setdefault('__collection__', i.__collection__)

        if not attr.get('__collection__'):
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            attr['__collection__'] = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

        attr['fields'].setdefault('_id', ObjectId)
        attr['_ruler'] = Node.make(attr['fields'])
        _cls = type.__new__(mcs, name, bases, attr)
        if attr['__database__']:
            Database.add(attr['__database__'],
                         attr['__uri__'],
                         attr['__connect_count__'])
            KnownClasses.add(_cls)
        return _cls


@six.add_metaclass(DocumentMeta)
class Document(object):
    __uri__ = DEFAULT_URI
    __database__ = None
    __collection__ = None
    __connect_count__ = DEFAULT_CONNECTIONS
    fields = {}
    roles = {}
    aliases = {}

    def __init__(self, *args, **kwargs):
        self._data = self._ruler()
        data = {}
        for i in args:
            data.update(i)
        data.update(kwargs)
        if data:
            self._data.set(data)

    def __setitem__(self, key, val):
        field = self.aliases.get(key, key)
        self._data[field] = val

    def __getitem__(self, key):
        field = self.aliases.get(key, key)
        if hasattr(self, field):
            return getattr(self, field)
        else:
            return self._data[field]

    def __delitem__(self, key):
        field = self.aliases.get(key, key)
        self._data.__delitem__(field)

    def __unicode__(self):
        return '%s(%s)' % (self.__class__.__name__, self._data['_id'])

    def __str__(self):
        return str(self.__unicode__())

    @property
    def pk(self):
        return self._data['_id'].value()

    @property
    def id(self):
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

    def setdefault(self, key, value):
        self._data.setdefault(key, value)

    @classmethod
    def get_cursor(cls, database=None, collection=None):
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
            if isinstance(_node, NodeComposite):
                yield self.preload(*_node.keys(), node=_node, cache=cache)

            elif isinstance(_node, NodeDocument):
                if k2 != '_id' and (not _node.been_set or _node.dirty):
                    dbref = _node.dbref
                    if dbref.id is not None:
                        data = cache.get(dbref)
                        if not data:
                            cur = self.get_cursor(dbref.database, dbref.collection)
                            data = yield cur.find_one(dbref.id, fields=_node.fields.keys())
                            cache[dbref] = data
                        _node.set(data)
                        _node.dirty_clear()
            else:
                yield self.preload(k2, node=_node, cache=cache)

    @coroutine
    def reread(self, *fields):
        """
        Read the object again. If the fields are not defined, all fields are read.
        :param fields: A list of field names
        """
        cur = self.get_cursor()
        _fields = fields or self.fields.keys()
        data = yield cur.find_one(self.pk, fields=_fields)
        if data:
            self._data.set(data)
            self.dirty_clear()

    @classmethod
    @coroutine
    def find_one_raw(cls, spec_or_id, *fields):
        cur = cls.get_cursor()
        data = yield cur.find_one(spec_or_id, fields=fields)
        raise Return(data)

    @classmethod
    @coroutine
    def find_one(cls, spec_or_id, preload=False):
        cur = cls.get_cursor()
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
    def find_raw(cls, spec, *fields):
        cur = cls.get_cursor()
        data = yield cur.find(spec, fields=fields)
        raise Return(data)

    @classmethod
    @coroutine
    def find(cls, spec=None, skip=0, limit=0, sort=None, hint=None, preload=False):
        cur = cls.get_cursor()
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
        cur = cls.get_cursor()
        data = yield cur.count(spec)
        raise Return(data)

    @classmethod
    @coroutine
    def distinct(cls, key, spec=None):
        cur = cls.get_cursor()
        data = yield cur.distinct(key, spec)
        raise Return(data)

    @coroutine
    def save(self, safe=True):
        self._data.setdefault('_id', ObjectId())
        if self._data.dirty:
            cur = self.get_cursor()
            res = yield cur.update({"_id": self._data['_id'].value()},
                                   self._data.query, upsert=True, safe=safe)
            if safe:
                if res:
                    self.dirty_clear()
                raise Return(res)

    @coroutine
    def remove(self, safe=True):
        cur = self.get_cursor()
        yield cur.remove(self['_id'].value(), safe)
        self['_id'] = None

    def fields_to_data(self, *roles):
        fields = set(itertools.chain(*[self.roles[i] for i in roles])
                     if roles else self.fields.keys())
        field_data = []
        for i in fields:
            x = self.aliases.get(i, i)
            field_data.append({'field': x,
                               'alias': i,
                               'attr': hasattr(self, x)})
        return field_data

    @coroutine
    def to_json_raw(self, field_data, cache):
        data = {}
        for i in field_data:
            if i['attr']:
                v = getattr(self, i['field'])
                if is_future(v):
                    v = yield v
            else:
                yield self.preload(i['field'], cache=cache)
                try:
                    v = self._data[i['field']]
                except (ValueError, AttributeError):
                    v = None
            if isinstance(v, Node):
                v = v.value()
            if v is not None:
                if isinstance(v, ObjectId):
                    v = str(v)
                elif isinstance(v, Document):
                    v = yield v.to_json(cache=cache)
            data[i['alias']] = v
        raise Return(data)

    @coroutine
    def to_json(self, *roles, **kwargs):
        """
        converts the attributes into a dictionary
        :param roles: Role name or list of role name. The role needs to be defined in the class
            attribute "roles".
        :return: dict
        """
        data = yield self.to_json_raw(self.fields_to_data(*roles),
                                      kwargs.get('cache', {}))
        raise Return(data)

    @classmethod
    @coroutine
    def from_json(cls, *args, **kwargs):
        # TODO: add role
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

# TODO: add cls.exists(spec)
# TODO: self.preload() не работает если модель {foo: {bar: cls}}
