# coding: utf-8

import re
from UserList import UserList

from bson import ObjectId, DBRef
from tornado.gen import coroutine, Return

from manage import ModelManager, DBManager

from errors import MokitoORMError
# from ruler import NodeDocument, NodeComposite
# from tools import SEPARATOR

DEFAULT_URI = "mongodb://127.0.0.1:27017"
DEFAULT_CONNECTIONS = 10


class Documents(UserList):
    def __repr__(self):
        return '<%s: [%s]>' % (self.__class__.__name__, ', '.join(map(str, self.data)))

    def dirty_clear(self):
        map(lambda i: i.dirty_clear(), self.data)

    # @coroutine
    # def reread(self, *fields):
    #     map(lambda i: (yield i.reread(*fields)), self.data)

    @coroutine
    def preload(self, *fields, **kwargs):
        cache = kwargs.get('cache', {})
        yield [i.preload(*fields, cache=cache) for i in self.data]

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
    def to_json(self, *roles):
        data = []
        if self.data:
            kwargs = {'cache': {}}
            data = [(yield i.to_json(*roles, **kwargs)) for i in self.data]
        raise Return(data)


class DocumentMeta(type):
    def __new__(mcs, name, bases, attr):
        if not attr.get('__collection__'):
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            attr['__collection__'] = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

        _cls = type.__new__(mcs, name, bases, attr)
        if name != 'Document':
            ModelManager.add(_cls)
            DBManager.add(_cls)
        return _cls


class Document(object):
    __metaclass__ = DocumentMeta
    __uri__ = DEFAULT_URI
    __database__ = None
    __collection__ = None
    __connect_count__ = DEFAULT_CONNECTIONS
    __model__ = None
    BY_ID_ERROR = 'Запись не найдена'

    def __init__(self, **data):
        self._id = data.pop('_id', None)
        self._data = self.__model__(data)

    def __setitem__(self, key, val):
        self._data.__setitem__(key, val)

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __delitem__(self, key):
        self._data.__delitem__(key)

    def __getattr__(self, item):
        return getattr(self._data, item)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self._id)

    @property
    def id(self):
        if self._id is not None:
            return str(self._id)

    @property
    def dbref(self):
        return DBRef(self.__collection__, self._id)

    @property
    def dirty(self):
        return self._data.dirty

    def dirty_clear(self):
        self._data.dirty_clear()

    # def is_dirty(self, *keys):
    #     return self._data.is_dirty(*keys)

    def get(self):
        return self._data.get()

    def set(self, value):
        self._data.set(value)

    value = property(get, set)

    # def setdefault(self, key, value):
    #     self._data.setdefault(key, value)

    @classmethod
    def get_cursor(cls, database=None, collection=None):
        db = database or cls.__database__
        try:
            return DBManager[db][collection or cls.__collection__]
        except KeyError:
            raise MokitoORMError('Connection to the database "%s" not found' % db)

    @coroutine
    def preload(self, *fields, **kwargs):
        pass
        # node = kwargs.get('node', self._data)
        # cache = kwargs.get('cache', {})
        #
        # fields = set(fields)
        # fields.discard('')
        # for i in fields:
        #     k1, _, k2 = str(i).partition(SEPARATOR)
        #     _node = node[k1]
        #     if isinstance(_node, NodeComposite):
        #         yield self.preload(*_node.keys(), node=_node, cache=cache)
        #
        #     elif isinstance(_node, NodeDocument):
        #         if k2 != '_id' and (not _node.been_set or _node.dirty):
        #             dbref = _node.dbref
        #             if dbref.id is not None:
        #                 data = cache.get(dbref)
        #                 if not data:
        #                     cur = self.get_cursor(dbref.database, dbref.collection)
        #                     data = yield cur.find_one(dbref.id, fields=_node.fields.keys())
        #                     cache[dbref] = data
        #                 _node.set(data)
        #                 _node.dirty_clear()
        #     else:
        #         yield self.preload(k2, node=_node, cache=cache)

    # @coroutine
    # def reread(self, *fields):
    #     """
    #     Read the object again. If the fields are not defined, all fields are read.
    #     :param fields: A list of field names
    #     """
    #     cur = self.get_cursor()
    #     _fields = fields or self.fields.keys()
    #     data = yield cur.find_one(self.pk, fields=_fields)
    #     if data:
    #         self._data.set(data)
    #         self.dirty_clear()

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
        fields = cls.__model__.fields.keys()
        data = yield cur.find_one(spec_or_id, fields=fields)
        if data:
            self = cls(**data)
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
        fields = cls.__model__.fields.keys()
        data = yield cur.find(spec, fields, skip, limit, sort=sort, hint=hint)
        res = Documents(cls(**i) for i in data)
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

    # @classmethod
    # @coroutine
    # def distinct(cls, key, spec=None):
    #     cur = cls.get_cursor()
    #     data = yield cur.distinct(key, spec)
    #     raise Return(data)

    @coroutine
    def save(self, safe=True):
        _s = False
        if self._id is None:
            self._id = ObjectId()
            _s = True
        if _s or self._data.dirty:
            cur = self.get_cursor()
            # res = yield cur.update({"_id": self._id},
            res = yield cur.update(self._id, self._data.query, upsert=True, safe=safe)
            if safe:
                if res:
                    self.dirty_clear()
                raise Return(res)

    # @coroutine
    # def remove(self, safe=True):
    #     cur = self.get_cursor()
    #     yield cur.remove(self['_id'].value(), safe)
    #     self['_id'] = None

    @coroutine
    def to_json(self, *roles, **kwargs):
        """
        converts the attributes into a dictionary
        :param roles: Role name or list of role name. The role needs to be defined in the class
            attribute "roles".
        :return: dict
        """
        kwargs.setdefault('cache', {})
        kwargs['document'] = self
        data = yield self._data.to_json(*roles, **kwargs)
        raise Return(data)

    # @classmethod
    # @coroutine
    # def from_json(cls, *args, **kwargs):
    #     # TODO: add role
    #     self = None
    #     data = {}
    #     for i in args:
    #         if isinstance(i, dict):
    #             data.update(i)
    #     data.update(kwargs)
    #
    #     _id = data.pop('_id', None)
    #     if _id:
    #         self = yield cls.find_one(_id)
    #     if not self:
    #         self = cls()
    #
    #     for k, v in data.items():
    #         try:
    #             self._data[k] = v
    #         except KeyError:
    #             pass
    #     raise Return(self)
