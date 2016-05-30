# coding: utf-8

import six
from UserList import UserList
from copy import copy
# from operator import attrgetter, getitem

from bson import ObjectId  # , DBRef, Code
from tornado.gen import coroutine, Return

from errors import InterfaceError
from dm import DM_dict

_all_clients = {}


class Documents(UserList):

    def __init__(self, data=None):
        self.data = data or []

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
        def mk_path(data):
            res = []
            for k, v in data.items():
                val = map(lambda i: '%s.%s' % (k, i), mk_path(v)) if isinstance(v, dict) else [k]
                res.extend(val)
            return res

        def convert(data):
            if data in (dict, tuple, list):
                data = data()

            if isinstance(data, dict):
                for k, v in data.items():
                    data[k] = convert(v)

            elif isinstance(data, list):
                if not len(data):
                    data = [None]
                else:
                    data = [convert(data[0])]

            elif isinstance(data, tuple):
                if not len(data):
                    data = (None,)
                else:
                    data = tuple(convert(i) for i in data)

            return data

        for i in ['__database__', '__collection__', 'fields', 'required', 'roles']:
            if i not in attr:
                for j in bases:
                    if hasattr(j, i):
                        attr[i] = getattr(j, i)
                        break

        convert(attr['fields'])
        attr['fields'].setdefault('_id', ObjectId)
        attr['_path'] = mk_path(attr['fields'])
        #attr['_dm'] = DM_dict(attr['fields'])
        _cls = type.__new__(cls, name, bases, attr)
        # _reg_classes[_cls.__module__.split('.')[0] + '.' + name] = _cls
        # if attr['Meta'].collection:
        #     _reg_collections[attr['Meta'].collection] = _cls
        return _cls


@six.add_metaclass(DocumentMeta)
class Document(object):
    __database__ = None
    __collection__ = None
    fields = {}
    required = []
    roles = {}

    @property
    def _id(self):
        return self._data['_id']

    def __init__(self, data=None):
        self._data = DM_dict(self.fields, data)

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
            return _all_clients[cls.__database__][cls.__collection__]
        except KeyError:
            raise InterfaceError('Connection to the database "%s" not found' % cls.__database__)

    def dirty_clear(self):
        self._data.dirty_clear()

    @classmethod
    @coroutine
    def find_one(cls, spec_or_id=None):
        cur = cls._cursor()
        data = yield cur.find_one(spec_or_id, fields=cls._path)
        if data:
            self = cls(data)
            self.dirty_clear()
            raise Return(self)

    @classmethod
    @coroutine
    def find(cls, spec=None, skip=0, limit=0, timeout=True, snapshot=False,
             tailable=False, sort=None, max_scan=None, slave_okay=False,
             hint=None, comment=None):
        cur = cls._cursor()
        data = yield cur.find(spec, cls._path, skip, limit, timeout, snapshot, tailable, sort, max_scan, slave_okay, False, hint, comment)
        res = Documents([cls(i) for i in data])
        res.dirty_clear()
        raise Return(res)

    @classmethod
    @coroutine
    def count(cls, spec=None):
        cur = cls._cursor()
        data = yield cur.count(spec)
        raise Return(data)

    def pre_save(self):
        pass

    @coroutine
    def save(self):
        self.pre_save()
        if self._data['_id'] is None:
            self._data['_id'] = ObjectId()

        data = self._data.dirty_data()
        if data:
            print 'SAVE-2', data
            cur = self._cursor()
            yield cur.update({"_id": self._data['_id']}, {"$set": data}, upsert=True)
            self.dirty_clear()

    def to_json(self, role=None, no_id=False):
        fields = set(self.roles[role] if role else self._path)
        if '_id' in fields:
            fields.remove('_id')

        data = {}
        _fields = []
        for i in fields:
            if hasattr(self, i):
                data[i] = getattr(self, i)
            else:
                _fields.append(i)

        data.update(self._data.inner_data(_fields))

        if not no_id:
            data['_id'] = str(self._id)

        return data

#     @classmethod
#     @coroutine
#     def from_json(cls, **kwargs):
#         self = None
#         _id = kwargs.pop('_id', None)
#         if _id:
#             self = yield cls.find_one(_id)
#         if not self:
#             self = cls()
#
#         for k, v in kwargs.items():
#             self[k] = v
#         raise Return(self)

if __name__ == "__main__":
    class Driver(Document):
        __collection__ = 'driver'
        fields = {
            'first_name': str,
            #'last_name': str,
            #'patronymic_name': str,

            # car
            #'car': {'number': str, 'hz': str},

            #"3c": {"3c1": int, "3c2": str, "3c3": dict, "3c4": {}},

            #"4d": list,
            "4d": [str],
            #"4g": [{"4a1": int, "4b1": str, "4c1": dict, "4d1": {}}],

            #"5a": (int, str, ),
        }
        required = ['first_name', 'last_name']

        @property
        def fio(self):
            return ' '.join((self['last_name'] or '', self['first_name'] or '', self['patronymic_name'] or ''))

        def __unicode__(self):
            return u'Driver(%s): %s %s' % (self['_id'], self['last_name'] or '', self['first_name'] or '')

#     x = {'first_name': 'F', 'last_name': 'L', 'patronymic_name': 'P', 'car': {'number': 123}}
#     d1 = Driver(**x)
#     print 'D1', d1
#     print 'D2', d1._data
#     print 'D3', d1._data['first_name']
#     print 'D4', d1['first_name']
#     d1['first_name'] = 'AssA'
#     d1['car.number'] = 12345
#     print 'D2', d1._data
#     print 'D1', d1
#     print 'D5', d1.fio

    #d = Driver()

    #d = Driver({"first_name": "AsA", 'car': {'number': 123, 'hz': 'djiga'}, "4d": [1, 2, 3]})
    d = Driver({"first_name": "AsA", "4d": [0, 1, 2]})
    print 'D1a', d
    print 'D2a', d._data
    print
    # print 'D31', d._data.dirty()
#     d.dirty_clear()
#     print 'XX1', d._data.dirty_data()
#     # print 'D32', d._data._dirty

    #d['first_name'] = 'QQ'
#     print
#     print 'D1b', d
#     print 'D2b', d._data
#     print 'D31', d._data._dirty

    # print 'D3', d['4d']
    # print 'D4', d['car']
    # print 'D4-1', d['car.number']
    #d['car.number'] = 456
#     print 'D4-2', d['car.number']
#     # print 'D31', d1._data._dirty
#     print 'XX2', d._data.dirty_data()

    # print 'X1b', d
    # print 'X2b', d._data
    # print 'X31', d._data._dirty
    # print 'X32', d._data.dirty()
    # d._data.dirty_clear()
    # print 'X32', d._data.dirty()
    # print 'X40', d._data.dirty_data()

    # print '4D1', d['4d']
    #d['4d'] = [4, 5, 6]
    # print '4D2', d['4d']
    # print '4D3', d._data

    # print '4D1', d['4d']
    #d['4d.1'] = 123
    # print '4D2', d['4d']
    # print '4D3', d._data

    print 'X40', d._data
    print 'X41', d._data.inner_data()
    # print 'X42', d._data.inner_data(['car.number', 'car.hz'])
    # print 'X42', d._data.inner_data(['car'])

    # print 'X42', d._data.inner_data(['4d'])
