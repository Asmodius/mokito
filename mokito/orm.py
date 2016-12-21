# coding: utf-8

from UserList import UserList

from bson import DBRef, ObjectId
from tornado.gen import coroutine, Return

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

    def __getattr__(self, item):
        return [getattr(i, item) for i in self.data]

    def dirty_clear(self):
        map(lambda i: i.dirty_clear(), self.data)

    # @coroutine
    # def reread(self, *fields):
    #     yield [i.reread(*fields) for i in self.data]

    # @property
    # def value(self):
    #     return [i.value for i in self.data]

    @coroutine
    def remove(self, safe=True):
        if self.data:
            ids = [i._id for i in self.data]
            cur = self.data[0].get_cursor()
            yield cur.remove({"_id": {"$in": ids}}, safe)
            for i in self.data:
                i._id = None

    def filter(self, fn):
        return Documents(filter(fn, self.data))

    def get(self, *fields, **kwargs):
        return [i.get(*fields, **kwargs) for i in self.data]


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

    def set(self, value, **kwargs):
        if isinstance(value, DBRef):
            self.dbref = value
        else:
            _id = value.pop('_id', None)
            if _id is not None:
                self._id = ObjectId(_id)
            self._data.set(value, **kwargs)

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
            yield [self._data[i].reread() for i in fields]

        else:
            cur = self.get_cursor()
            data = yield cur.find_one(self._id, fields=self.fields.keys())
            if data:
                self.clear()
                self.set(data, inner=True)
                self.dirty_clear()
                raise Return(True)

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
        fields = cls.fields.keys()
        data = yield cur.find_one(spec_or_id, fields=fields)
        if data:
            self = cls(data, inner=True)
            self._data.dirty_clear()
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
    def find(cls, spec=None, skip=0, limit=0, sort=None, hint=None):
        cur = cls.get_cursor()
        fields = cls.fields.keys()
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
