import copy
from collections import UserList

from bson import DBRef, ObjectId

from .models import Model
from .errors import MokitoORMError
from .tools import SEPARATOR


class Documents(UserList):
    def __repr__(self):
        return '<%s: [%s]>' % (self.__class__.__name__, ', '.join(map(str, self.data)))

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        ret = self.data[int(k1)]
        return ret[k2] if k2 else ret

    # def __call__(self, method_name, *args, **kwargs):
    #     return [getattr(i, method_name)(*args, **kwargs) for i in self.data]

    # def dirty_clear(self):
    #     map(lambda i: i.dirty_clear(), self.data)

    # @coroutine
    # def reread(self, *fields):
    #     # TODO: добавить кэш
    #     yield [i.reread(*fields) for i in self.data]

    async def remove(self, safe=True):
        if self.data:
            ids = [i.id for i in self.data]
            await self.data[0].get_collection().delete_many({"_id": {"$in": ids}})
            for i in self.data:
                i.id = None

    async def save(self):
        for i in self.data:
            await i.save()

    # def filter(self, fn):
    #     return Documents(filter(fn, self.data))

    def get_value(self, **kwargs):
        return [i.get_value(**kwargs) for i in self.data]

    value = property(get_value)


class Result(object):
    def __init__(self, cls, db_cursor):
        self.cls = cls
        self.db_cursor = db_cursor

    def __aiter__(self):
        return self

    async def __anext__(self):
        if await self.db_cursor.fetch_next:
            data = self.db_cursor.next_object()
            return self.cls.mk(data)
        raise StopAsyncIteration

    async def all(self):
        return Documents([self.cls.mk(data) async for data in self.db_cursor])


class Document(Model):
    __database__ = None
    __collection__ = None
    BY_ID_ERROR = 'Запись не найдена'

    def __init__(self, data=None, **kwargs):
        self.loaded = False
        self.ref_changed = False
        self._id = None
        if data:
            _id = data.pop('_id', None)
            if _id:
                self._id = ObjectId(_id)
        super().__init__(data, **kwargs)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self._id)

    # def __call__(self, method_name, *args, **kwargs):
    #     return getattr(self, method_name)(*args, **kwargs)

    @property
    def self_value(self):
        return self.get_dbref() if self._id else None

    def _set_parent_dirty(self):
        self._dirty = True
        self.ref_changed = True
        if self._parent is not None:
            self._parent._dirty = True

    def get_id(self):
        return self._id

    def set_id(self, value):
        if value is not None:
            value = ObjectId(value)
        if self._id != value:
            self._id = value
            self._set_parent_dirty()

    id = property(get_id, set_id)

    def get_dbref(self):
        return DBRef(self.__collection__, self._id)

    def set_dbref(self, dbref):
        if self.__collection__ != dbref.collection:
            self.__collection__ = dbref.collection
            self._set_parent_dirty()
        self.set_id(dbref.id)

    dbref = property(get_dbref, set_dbref)

    @classmethod
    def mk(cls, data):
        self = cls(data, inner=True)
        self.dirty_clear()
        self.loaded = True
        return self

    def clear(self):
        super().clear()
        self._id = None

    def dirty_clear(self):
        super().dirty_clear()
        self.ref_changed = False

    def get_value(self, **kwargs):
        data = super().get_value(**kwargs)
        data['_id'] = self._id
        return data

    def set_value(self, value, **kwargs):
        if isinstance(value, DBRef):
            self.dbref = value
        else:
            if isinstance(value, dict):
                value = copy.deepcopy(value)
                _id = value.pop('_id', None)
                if _id is not None:
                    self._id = ObjectId(_id)
            super().set_value(value, **kwargs)

    value = property(get_value, set_value)

    @classmethod
    def get_collection(cls, database=None, collection=None):
        return (database or cls.__database__)[collection or cls.__collection__]

    @staticmethod
    def _norm_spec(spec):
        if spec is None:
            return {}

        if isinstance(spec, bytes):
            return {"_id": ObjectId(spec.decode('utf-8'))}

        if isinstance(spec, str):
            return {"_id": ObjectId(spec)}

        if isinstance(spec, ObjectId):
            return {"_id": spec}

        return spec

    @classmethod
    async def by_id(cls, _id):
        if _id:
            try:
                self = await cls.find_one(_id)
            except:
                self = None
            if self:
                return self
        raise MokitoORMError(cls.BY_ID_ERROR)

    # @classmethod
    # @coroutine
    # def find_one_raw(cls, spec_or_id, *fields):
    #     data = yield cls.get_collection().find_one(spec_or_id, fields=fields)
    #     raise Return(data)

    @classmethod
    async def find_one(cls, spec_or_id):
        spec = cls._norm_spec(spec_or_id)
        data = await cls.get_collection().find_one(spec, list(cls.scheme.keys()))
        if data:
            return cls.mk(data)

    # @classmethod
    # @coroutine
    # def find_raw(cls, spec, *fields, **kwargs):
    #     kw = {
    #         'fields': fields,
    #         'skip': kwargs.get('skip', 0),
    #         'limit': kwargs.get('limit', 0),
    #         'sort': kwargs.get('sort'),
    #         'hint': kwargs.get('hint')
    #     }
    #     data = yield cls.get_collection().find(spec, **kw)
    #     raise Return(data)

    @classmethod
    def find(cls, spec_or_id=None, skip=0, limit=0, sort=None, hint=None):
        spec = cls._norm_spec(spec_or_id)
        cursor = cls.get_collection().find(spec, list(cls.scheme.keys()), skip=skip, limit=limit)
        return Result(cls, cursor)

    @classmethod
    async def count(cls, spec=None):
        spec = cls._norm_spec(spec)
        return await cls.get_collection().count(spec)

    @classmethod
    async def distinct(cls, key, spec=None):
        spec = cls._norm_spec(spec)
        return await cls.get_collection().distinct(key, spec)

    async def reread(self, *fields):
        """
        Read the object again.
        """
        if fields:
            return any([await self[i].reread() for i in fields])

        elif self._id:
            data = await self.get_collection().find_one({'_id': self._id}, list(self.scheme.keys()))
            if data:
                self.clear()
                self.set_value(data, inner=True)
                self.dirty_clear()
                self.loaded = True
                return True

    async def save(self):
        if self._id is None:
            res = await self.get_collection().insert_one(super().self_value)
            self._id = res.inserted_id
            self.dirty_clear()
            return True

        elif self.dirty:
            await self.get_collection().update_one({'_id': self._id}, self.query)
            self.dirty_clear()
            return True

    async def remove(self):
        await self.get_collection().delete_one({'_id': self._id})
        self._id = None
