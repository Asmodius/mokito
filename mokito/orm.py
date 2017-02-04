# coding: utf-8

from UserList import UserList

from bson import DBRef, ObjectId
from tornado.gen import coroutine, Return

from manage import ModelManager
from fields import DictField
from errors import MokitoORMError

from tools import SEPARATOR

DEFAULT_URI = "mongodb://127.0.0.1:27017"
DEFAULT_CONNECTIONS = 10


class ModelMeta(type):
    def __new__(mcs, name, bases, attr):
        scheme = attr.get('scheme')
        if scheme is not None and not isinstance(scheme, dict):
            attr['scheme'] = getattr(scheme, 'scheme')

        _cls = type.__new__(mcs, name, bases, attr)
        if name != 'Model' and name != 'Document':
            ModelManager.add(_cls)
        return _cls


class Model(DictField):
    __metaclass__ = ModelMeta
    scheme = {}

    def __init__(self, data=None, **kwargs):
        super(Model, self).__init__(self.scheme)
        if data:
            self.set(data, **kwargs)

    def get(self, key=None, **kwargs):
        if isinstance(key, (list, tuple)):
            data = {}
            fields = []
            for i in key:
                if hasattr(self, i):
                    data[i] = getattr(self, i)
                else:
                    fields.append(i)
            return dict(super(Model, self).get(fields, **kwargs), **data)

        return super(Model, self).get(key, **kwargs)


class Documents(UserList):
    def __repr__(self):
        return '<%s: [%s]>' % (self.__class__.__name__, ', '.join(map(str, self.data)))

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        ret = self.data[int(k1)]
        return ret[k2] if k2 else ret

    def __call__(self, method_name, *args, **kwargs):
        return [getattr(i, method_name)(*args, **kwargs) for i in self.data]

    def dirty_clear(self):
        map(lambda i: i.dirty_clear(), self.data)

    @coroutine
    def reread(self, *fields):
        # TODO: добавить кэш
        yield [i.reread(*fields) for i in self.data]

    @coroutine
    def remove(self, safe=True):
        if self.data:
            ids = [i._id for i in self.data]
            cur = self.data[0].get_cursor()
            yield cur.remove({"_id": {"$in": ids}}, safe)
            for i in self.data:
                i._id = None

    @coroutine
    def save(self, safe=True):
        yield [i.save(safe) for i in self.data]

    def filter(self, fn):
        return Documents(filter(fn, self.data))

    def get(self, key, **kwargs):
        return [i.get(key, **kwargs) for i in self.data]


class Document(Model):
    __uri__ = DEFAULT_URI
    __database__ = None
    __collection__ = None
    __connect_count__ = DEFAULT_CONNECTIONS
    BY_ID_ERROR = 'Запись не найдена'

    def __init__(self, data=None, **kwargs):
        self.loaded = False
        self._id = None
        if data:
            _id = data.pop('_id', None)
            if _id:
                self._id = ObjectId(_id)
        super(Document, self).__init__(data, **kwargs)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self._id)

    def __call__(self, method_name, *args, **kwargs):
        return getattr(self, method_name)(*args, **kwargs)

    @property
    def self_value(self):
        return self.get_dbref() if self._id else None

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

    def clear(self):
        super(Document, self).clear()
        self._id = None

    def set(self, value, **kwargs):
        if isinstance(value, DBRef):
            self.dbref = value
        else:
            value = value.copy()
            _id = value.pop('_id', None)
            if _id is not None:
                self._id = ObjectId(_id)
            super(Document, self).set(value, **kwargs)

    @classmethod
    def get_cursor(cls, database=None, collection=None):
        db = database or cls.__database__
        try:
            return ModelManager.databases[db][collection or cls.__collection__]
        except KeyError:
            raise MokitoORMError('Connection to the database "%s" not found' % db)

    @coroutine
    def reread(self, *fields):
        """
        Read the object again.
        """
        if fields:
            yield [self[i].reread() for i in fields]

        elif self._id:
            cur = self.get_cursor()
            data = yield cur.find_one(self._id, fields=self.scheme.keys())
            if data:
                self.clear()
                self.set(data, inner=True)
                self.dirty_clear()
                self.loaded = True
                raise Return(True)

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
    def find_one_raw(cls, spec_or_id, *fields):
        cur = cls.get_cursor()
        data = yield cur.find_one(spec_or_id, fields=fields)
        raise Return(data)

    @classmethod
    @coroutine
    def find_one(cls, spec_or_id):
        cur = cls.get_cursor()
        fields = cls.scheme.keys()
        data = yield cur.find_one(spec_or_id, fields=fields)
        if data:
            self = cls(data, inner=True)
            self.dirty_clear()
            self.loaded = True
            raise Return(self)

    @classmethod
    @coroutine
    def find_raw(cls, spec, *fields, **kwargs):
        cur = cls.get_cursor()
        kw = {
            'fields': fields,
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 0),
            'sort': kwargs.get('sort'),
            'hint': kwargs.get('hint')
        }
        data = yield cur.find(spec, **kw)
        raise Return(data)

    @classmethod
    @coroutine
    def find(cls, spec=None, skip=0, limit=0, sort=None, hint=None):
        cur = cls.get_cursor()
        fields = cls.scheme.keys()
        data = yield cur.find(spec, fields, skip, limit, sort=sort, hint=hint)
        res = Documents(cls(i, inner=True) for i in data)
        res.dirty_clear()
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
        if self._id is None:
            cur = self.get_cursor()
            self._id = yield cur.insert(super(Document, self).self_value, safe=safe)
            self.dirty_clear()
            if safe:
                raise Return(True)

        elif self.dirty:
            cur = self.get_cursor()
            res = yield cur.update(self._id, self.query, safe=safe)
            if res:
                self.dirty_clear()
                if safe:
                    raise Return(res)

    @coroutine
    def remove(self, safe=True):
        cur = self.get_cursor()
        yield cur.remove(self._id, safe)
        self._id = None
