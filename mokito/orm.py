# coding: utf-8

import copy
from UserList import UserList

from bson import DBRef, ObjectId
from tornado.gen import coroutine, Return
from tornado.concurrent import is_future

from manage import ModelManager
from model import Model
from errors import MokitoORMError

from tools import SEPARATOR

DEFAULT_URI = "mongodb://127.0.0.1:27017"
DEFAULT_CONNECTIONS = 10


class Documents(UserList):
    def __repr__(self):
        return '<%s: [%s]>' % (self.__class__.__name__, ', '.join(map(str, self.data)))

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        ret = self.data[int(k1)]
        return ret[k2] if k2 else ret

    def dirty_clear(self):
        map(lambda i: i.dirty_clear(), self.data)

    @coroutine
    def reread(self, *fields):
        map(lambda i: (yield i.reread(*fields)), self.data)

    @coroutine
    def preload(self, *fields, **kwargs):
        cache = kwargs.get('cache', {})
        yield [i.preload(*fields, cache=cache) for i in self.data]

    @property
    def value(self):
        return [i.value for i in self.data]

#     @coroutine
#     def remove(self, safe=True):
#         if self.data:
#             ids = [i.pk for i in self.data]
#             cur = self.data[0].get_cursor()
#             yield cur.remove({"_id": {"$in": ids}}, safe)
#             for i in self.data:
#                 i['_id'] = None

    def filter(self, fn):
        return Documents(filter(fn, self.data))

    @coroutine
    def get(self, fields=None, aliases=None, **kwargs):
        # data = [(yield i.get(fields,  aliases, **kwargs)) for i in self.data]
        data = yield [i.get(fields, aliases, **kwargs) for i in self.data]
        raise Return(data)

    # @coroutine
    # def to_json(self, *roles):
    #     data = []
    #     if self.data:
    #         kwargs = {'cache': {}}
    #         data = [(yield i.to_json(*roles, **kwargs)) for i in self.data]
    #     raise Return(data)


class Document(Model):
    __uri__ = DEFAULT_URI
    __database__ = None
    __collection__ = None
    __connect_count__ = DEFAULT_CONNECTIONS
    BY_ID_ERROR = 'Запись не найдена'

    def __init__(self, data=None, **kwargs):
        self._id = None
        if data:
            _id = data.pop('_id', None)
            if _id:
                self._id = ObjectId(_id)
        super(Document, self).__init__(data, **kwargs)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self._id)

    @property
    def id(self):
        if self._id is not None:
            return str(self._id)

    def get_dbref(self):
        return DBRef(self.__collection__, self._id)

    def set_dbref(self, dbref):
        self.__collection__ = dbref.collection
        self._id = dbref.id

    dbref = property(get_dbref, set_dbref)

    @property
    def dirty(self):
        return self._data.dirty

    def dirty_clear(self):
        self._data.dirty_clear()

    def clear(self):
        self._id = None
        self._data.clear()

    @coroutine
    def get(self, fields=None, aliases=None, **kwargs):
        data1 = {}
        if fields:
            if aliases is None:
                aliases = {}
            _fields = []
            for i in fields:
                if hasattr(self, i):
                    v = getattr(self, i)
                    if is_future(v):
                        v = yield v
                    if kwargs.get('as_json') and isinstance(v, ObjectId):
                        v = str(v)
                    data1[aliases.get(i, i)] = v
                else:
                    _fields.append(i)
        else:
            _fields = fields
        raise Return(dict(self._data.get(_fields, aliases, **kwargs), **data1))

    def set(self, value, aliases=None, **kwargs):
        if isinstance(value, DBRef):
            self.dbref = value
        else:
            _id = value.pop('_id', None)
            if _id is not None:
                self._id = ObjectId(_id)
            self._data.set(value, aliases, **kwargs)

    @classmethod
    def get_cursor(cls, database=None, collection=None):
        db = database or cls.__database__
        try:
            return ModelManager.databases[db][collection or cls.__collection__]
        except KeyError:
            raise MokitoORMError('Connection to the database "%s" not found' % db)

    @coroutine
    def preload(self, *fields, **kwargs):
        print 'PRE'
    #     # node = kwargs.get('node', self._data)
    #     # cache = kwargs.get('cache', {})
    #     #
    #     # fields = set(fields)
    #     # fields.discard('')
    #     # for i in fields:
    #     #     k1, _, k2 = str(i).partition(SEPARATOR)
    #     #     _node = node[k1]
    #     #     if isinstance(_node, NodeComposite):
    #     #         yield self.preload(*_node.keys(), node=_node, cache=cache)
    #     #
    #     #     elif isinstance(_node, NodeDocument):
    #     #         if k2 != '_id' and (not _node.been_set or _node.dirty):
    #     #             dbref = _node.dbref
    #     #             if dbref.id is not None:
    #     #                 data = cache.get(dbref)
    #     #                 if not data:
    #     #                     cur = self.get_cursor(dbref.database, dbref.collection)
    #     #                     data = yield cur.find_one(dbref.id, fields=_node.fields.keys())
    #     #                     cache[dbref] = data
    #     #                 _node.set(data)
    #     #                 _node.dirty_clear()
    #     #     else:
    #     #         yield self.preload(k2, node=_node, cache=cache)

    @coroutine
    def reread(self):
        """
        Read the object again.
        """
        cur = self.get_cursor()
        data = yield cur.find_one(self._id, fields=self.fields.keys())
        if data:
            self.clear()
            self.set(data, inner=True)
            self.dirty_clear()
            raise Return(True)

    # @classmethod
    # @coroutine
    # def find_one_raw(cls, spec_or_id, *fields):
    #     cur = cls.get_cursor()
    #     data = yield cur.find_one(spec_or_id, fields=fields)
    #     raise Return(data)

    @classmethod
    @coroutine
    def find_one(cls, spec_or_id, preload=False):
        cur = cls.get_cursor()
        fields = cls.fields.keys()
        data = yield cur.find_one(spec_or_id, fields=fields)
        if data:
            self = cls(data, inner=True)
            self._data.dirty_clear()
            if preload:
                yield self.preload(*fields)
            raise Return(self)

    @classmethod
    @coroutine
    def by_id(cls, _id):
        if _id:
            try:
                self = yield cls.find_one(_id)
            except:
                self = None
            if self:
                raise Return(self)
        raise MokitoORMError(cls.BY_ID_ERROR)

    # @classmethod
    # @coroutine
    # def find_raw(cls, spec, *fields):
    #     cur = cls.get_cursor()
    #     data = yield cur.find(spec, fields=fields)
    #     raise Return(data)

    @classmethod
    @coroutine
    def find(cls, spec=None, skip=0, limit=0, sort=None, hint=None, preload=False):
        cur = cls.get_cursor()
        fields = cls.fields.keys()
        data = yield cur.find(spec, fields, skip, limit, sort=sort, hint=hint)
        res = Documents(cls(i, inner=True) for i in data)
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
        if self.dirty:
            q = self._data.query
            cur = self.get_cursor()

            if self._id is None:
                self._id = yield cur.insert(self._data.value, safe)
                self.dirty_clear()
                if safe:
                    raise Return(True)
            else:
                res = yield cur.update(self._id, q, safe=safe)
                if res:
                    self.dirty_clear()
                    if safe:
                        raise Return(res)

    @coroutine
    def remove(self, safe=True):
        cur = self.get_cursor()
        yield cur.remove(self._id, safe)
        self._id = None

    # @coroutine
    # def to_json(self, *roles, **kwargs):
    #     """
    #     converts the attributes into a dictionary
    #     :param roles: Role name or list of role name. The role needs to be defined in the class
    #         attribute "roles".
    #     :return: dict
    #     """
    #     kwargs.setdefault('cache', {})
    #     kwargs['document'] = self
    #     data = yield self._data.to_json(*roles, **kwargs)
    #     raise Return(data)
    #
    # # @classmethod
    # # @coroutine
    # # def from_json(cls, *args, **kwargs):
    # #     # TODO: add role
    # #     self = None
    # #     data = {}
    # #     for i in args:
    # #         if isinstance(i, dict):
    # #             data.update(i)
    # #     data.update(kwargs)
    # #
    # #     _id = data.pop('_id', None)
    # #     if _id:
    # #         self = yield cls.find_one(_id)
    # #     if not self:
    # #         self = cls()
    # #
    # #     for k, v in data.items():
    # #         try:
    # #             self._data[k] = v
    # #         except KeyError:
    # #             pass
    # #     raise Return(self)
