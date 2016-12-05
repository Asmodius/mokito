# coding: utf-8

import itertools
import inspect
import datetime
import copy
from collections import OrderedDict

try:
    import ujson as json
except ImportError:
    import json
import pytz
from dateutil.parser import parse
from bson import ObjectId, DBRef
from tornado.gen import coroutine, Return
from tornado.concurrent import is_future

from manage import ModelManager

# TODO: add class for DBRef


SEPARATOR = '.'


class Field(object):
    def __init__(self, *args):
        self._val = None
        self._dirty = False

    @property
    def dirty(self):
        return self._dirty

    def dirty_clear(self):
        self._dirty = False

    @staticmethod
    def convert(value):
        return value

    def get(self):
        return self._val

    def set(self, value):
        if not (value is None or isinstance(value, self._val.__class__)):
            value = self.convert(value)
        res = self._val != value
        if res:
            self._val = value
            self._dirty = True

    value = property(get, set)

    def to_json(self, *args, **kwargs):
        return self._val

    def from_json(self, value, **params):
        _value = params.get('_value')
        if _value is None and isinstance(value, basestring):
            _value = json.loads(value)
        self.set(_value)

    @classmethod
    def make(cls, rules=None):
        from orm import Document

        if rules is None:
            return Field()
        else:
            _type = rules if inspect.isclass(rules) else type(rules)
            if _type is int:
                return IntField()
            if _type is float:
                return FloatField()
            if _type is str:
                return StringField()
            if _type is unicode:
                return StringField()
            if _type is bool:
                return BooleanField()
            if _type is ObjectId:
                return ObjectIdField()
            if _type is datetime.datetime:
                return DateTimeField()
            if _type is list:
                return ListField(rules)
            if _type is tuple:
                return TupleField(rules)
            if _type is dict:
                return DictField(rules)
            if issubclass(_type, Model):
                return _type()

            if issubclass(_type, Document):
                print 'RTY', rules
                return DocumentField()

            if issubclass(_type, Field):
                return _type(rules)
            raise TypeError()

    def setdefault(self, value):
        if self._val is None:
            self.set(value)

    def clear(self):
        self._val = None
        self._dirty = True

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.get())


class IntField(Field):
    @staticmethod
    def convert(value):
        return int(value)


class FloatField(Field):
    @staticmethod
    def convert(value):
        return float(value)


class StringField(Field):
    @staticmethod
    def convert(value):
        # TODO: add unicode -> str
        return str(value)

    def __getitem__(self, key):
        return self._val[int(key)]


class BooleanField(Field):
    @staticmethod
    def convert(value):
        return bool(value)


class ObjectIdField(Field):
    @staticmethod
    def convert(value):
        return ObjectId(value)

    def to_json(self, *args, **kwargs):
        if self._val is not None:
            return str(self._val)


class DateTimeField(Field):
    # @staticmethod
    # def convert(value):
    #     return int(value)

    def to_json(self, *args, **kwargs):
        """
        :param kwargs:
            _format:  string for strftime
            without_microsecond:  bool
            tz:  pytz.timezone('Asia/Novosibirsk')
            tz_name: 'Asia/Novosibirsk'
        """
        if self._val is not None:
            tz_name = kwargs.get('tz_name')
            tz = pytz.timezone(tz_name) if tz_name else kwargs.get('tz')
            val = tz.fromutc(self._val) if tz else self._val
            if kwargs.get('without_microsecond', True):
                val = val.replace(microsecond=0)
            _format = kwargs.get('_format')
            return val.strftime(_format) if _format else val.isoformat()

    def from_json(self, value, _format=None, **params):
        _value = params.get('_value')
        if _value is None and isinstance(value, basestring):
            _value = json.loads(value)
        if _value is not None:
            if _format:
                _value = datetime.datetime.strptime(_value, _format)
            else:
                _value = parse(_value).replace(tzinfo=None)
        self.set(_value)


class CollectionField(Field):
    def dirty_clear(self):
        self._dirty = False
        for i in self._val.values():
            i.dirty_clear()

    def _set(self, k1, k2, value):
        if k2:
            self._val[k1].__setitem__(k2, value)
        else:
            try:
                self._val[k1].set(value)
            except KeyError:
                raise IndexError(k1)

    @property
    def dirty(self):
        if not self._dirty:
            self._dirty = any(i.dirty for i in self._val.values())
        return self._dirty


class ArrayField(CollectionField):
    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        try:
            k1 = int(k1)
            ret = self._val[k1]
            return ret[k2] if k2 else ret
        except KeyError:
            raise IndexError(k1)

    def __len__(self):
        return max(list(self._val.keys())) + 1 if self._val else 0

    def get(self):
        return [self._val[i].get() if i in self._val else None for i in range(len(self))]

    def set(self, value):
        self.clear()
        if value is not None:
            for k, v in enumerate(value):
                self.__setitem__(k, v)

    value = property(get, set)

    @property
    def query(self):
        return {'$set': self.value} if self.dirty else {}

    def to_json(self, *args, **kwargs):
        key_param = {}
        all_param = {}
        for k, v in kwargs.items():
            k1, _, k2 = str(k).partition(SEPARATOR)
            if k2:
                try:
                    k1 = int(k1)
                    key_param.setdefault(k1, {})
                    key_param[k1][k2] = v
                except ValueError:
                    all_param[k] = v
            else:
                all_param[k1] = v

        if args:
            fields = OrderedDict()
            for k in args:
                k1, _, k2 = str(k).partition(SEPARATOR)
                k1 = int(k1)
                fields.setdefault(k1, [])
                if k2 and k2 not in fields[k1]:
                    fields[k1].append(k2)
        else:
            fields = OrderedDict({i: [] for i in range(len(self))})

        res = []
        for k1, k2 in fields.items():
            if k1 in self._val:
                x = key_param.get(k1, {})
                x.update(all_param)
                res.append(self._val[k1].to_json(*k2, **x))
            else:
                res.append(None)
        return res


class ListField(ArrayField):
    def __init__(self, rules):
        super(ListField, self).__init__()
        self._rules = Field.make((rules+[None])[0])
        self._val = {}

    def __setitem__(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        if k1 not in self._val:
            self._val[k1] = copy.deepcopy(self._rules)
        self._set(k1, k2, value)

    def __delitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        if k2:
            self._val[k1].__delitem__(k2)
            self._dirty = True
        else:
            self.pop(k1)

    def clear(self):
        self._val = {}
        self._dirty = True

    def from_json(self, value, **params):
        _value = params.pop('_value', None)
        if _value is None and isinstance(value, basestring):
            _value = json.loads(value)

        self.clear()
        if _value is not None:
            key_param = {}
            all_param = {}
            for k, v in params.items():
                k1, _, k2 = str(k).partition(SEPARATOR)
                if k2:
                    try:
                        k1 = int(k1)
                        key_param.setdefault(k1, {})
                        key_param[k1][k2] = v
                    except ValueError:
                        all_param[k] = v
                else:
                    all_param[k1] = v

            for k, v in enumerate(_value):
                x = key_param.get(k, {})
                x.update(all_param)
                self._val[k] = copy.deepcopy(self._rules)
                self._val[k].from_json(None, _value=v, **x)

    def append(self, value):
        self.__setitem__(len(self), value)
        self._dirty = True

    def pop(self, key=-1, default=None):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if k2:
            return self._val[k1].pop(k2)

        k1 = int(k1)
        if k1 < 0:
            k1 += len(self)

        ret = copy.deepcopy(self._rules)
        ret.set(default)
        keys = list(self._val.keys())
        keys.sort()
        for i in keys:
            if k1 == i:
                ret = self._val[i]
                self._dirty = True
                del self._val[i]
            elif k1 < i:
                self._val[i-1] = self._val[i]
                self._dirty = True
                del self._val[i]
        return ret


class TupleField(ArrayField):
    def __init__(self, rules):
        super(TupleField, self).__init__()
        self._val = {k: Field.make(v) for k, v in enumerate(rules)}

    def __setitem__(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        self._set(int(k1), k2, value)

    def __delitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        if k2:
            self._val[k1].__delitem__(k2)
        else:
            self._val[k1].clear()
        self._dirty = True

    def clear(self):
        for i in self._val.values():
            i.clear()
        self._dirty = True

    def from_json(self, value, **params):
        _value = params.pop('_value', None)
        if _value is None and isinstance(value, basestring):
            _value = json.loads(value)

        self.clear()
        if _value is not None:
            key_param = {}
            all_param = {}
            for k, v in params.items():
                k1, _, k2 = str(k).partition(SEPARATOR)
                if k2:
                    try:
                        k1 = int(k1)
                        key_param.setdefault(k1, {})
                        key_param[k1][k2] = v
                    except ValueError:
                        all_param[k] = v
                else:
                    all_param[k1] = v

            for i, j in enumerate(_value):
                x = key_param.get(i, {})
                x.update(all_param)
                self._val[i].from_json(None, _value=j, **x)


class DictField(CollectionField):
    def __init__(self, rules):
        super(DictField, self).__init__()
        if rules:
            self._rules = True
            self._val = {k: self.make(v) for k, v in rules.items()}
        else:
            self._rules = False
            self._val = {}

    def get(self):
        return {k: v.get() for k, v in self._val.items()}

    def set(self, value):
        self.clear()
        for k, v in value.items():
            self.__setitem__(k, v)

    value = property(get, set)

    def to_json(self, *args, **kwargs):
        key_param = {}
        all_param = {}
        for k, v in kwargs.items():
            k1, _, k2 = str(k).partition(SEPARATOR)
            if k2:
                key_param.setdefault(k1, {})
                key_param[k1][k2] = v
            else:
                all_param[k1] = v

        if args:
            fields = {}
            for k in args:
                k1, _, k2 = str(k).partition(SEPARATOR)
                fields.setdefault(k1, [])
                if k2 and k2 not in fields[k1]:
                    fields[k1].append(k2)
        else:
            fields = {i: [] for i in self._val.keys()}

        res = {}
        for k1, k2 in fields.items():
            if k1 in self._val:
                res[k1] = self._val[k1].to_json(*k2, **dict(key_param.get(k1, {}), **all_param))
            else:
                res[k1] = None
        return res

    def from_json(self, value, **params):
        _value = params.pop('_value', None)
        if _value is None and isinstance(value, basestring):
            _value = json.loads(value)

        self.clear()
        if _value is not None:
            key_param = {}
            all_param = {}
            for k, v in params.items():
                k1, _, k2 = str(k).partition(SEPARATOR)
                if k2:
                    key_param.setdefault(k1, {})
                    key_param[k1][k2] = v
                else:
                    all_param[k1] = v

            for k, v in _value.items():
                x = key_param.get(k, {})
                x.update(all_param)
                if not self._rules:
                    self._val[k] = Field.make(v)
                self._val[k].from_json(None, _value=v, **x)

    def clear(self):
        self._dirty = True
        if self._rules:
            for i in self._val.values():
                i.clear()
        else:
            self._val = {}

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        ret = self._val.get(k1)
        return ret[k2] if k2 else ret

    def __setitem__(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if not self._rules:
            self._val[k1] = Field.make(value)
        self._set(k1, k2, value)

    def __delitem__(self, key):
        self._dirty = True
        k1, _, k2 = str(key).partition(SEPARATOR)
        if k2:
            del self._val[k1][k2]
        elif not self._rules:
            del self._val[k1]
        else:
            self._val[k1].clear()

    @property
    def query(self):
        from orm import Document

        ret = {"$set": {}, "$unset": {}}

        if not self._rules:
            ret['$set'] = self.value

        else:
            for k, v in self._val.items():
                if v.dirty:
                    if isinstance(v, Document):
                        print 'NodeDocument!!'
                        # ref = v.dbref
                        # ret["$set"][i] = ref if ref.id else None

                    elif isinstance(v, ArrayField):
                        _q = v.query
                        for j in ["$set", "$unset"]:
                            if j in _q:
                                ret[j][k] = _q[j]

                    elif isinstance(v, DictField):
                        _q = v.query
                        for j in ["$set", "$unset"]:
                            if j in _q:
                                if v._rules:
                                    for k1, v1 in _q[j].items():
                                        ret[j]["%s.%s" % (k, k1)] = v1
                                else:
                                    ret[j][k] = _q[j]

                    elif isinstance(v, Model):
                        _q = v.query
                        for j in ["$set", "$unset"]:
                            if j in _q:
                                for k1, v1 in _q[j].items():
                                    ret[j]["%s.%s" % (k, k1)] = v1

                    else:
                        ret['$set'][k] = v.value

        if not ret["$set"]:
            del ret["$set"]
        if not ret["$unset"]:
            del ret["$unset"]
        return ret


class DocumentField(object):
    pass


class ModelMeta(type):
    def __new__(mcs, name, bases, attr):
        _cls = type.__new__(mcs, name, bases, attr)
        if name != 'Model':
            ModelManager.add(_cls)
        return _cls


class Model(object):
    __metaclass__ = ModelMeta
    fields = {}
    aliases = {}

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._data.get())

    def __init__(self, *args, **kwargs):
        self._data = copy.deepcopy(self._f)
        data = {}
        for i in args:
            data.update(i)
        data.update(kwargs)
        if data:
            self._data.set(data)

    def __getitem__(self, key):
        key = self.aliases.get(key, key)
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return self._data.__getitem__(key)

    def __setitem__(self, key, value):
        self._data.__setitem__(self.aliases.get(key, key), value)

    def __delitem__(self, key):
        self._data.__delitem__(self.aliases.get(key, key))

    def get(self):
        return self._data.get()

    def set(self, value):
        self._data.set(value)

    value = property(get, set)

    @property
    def dirty(self):
        return self._data.dirty

    @property
    def query(self):
        return self._data.query

    def clear(self):
        self._data.clear()

    def dirty_clear(self):
        self._data.dirty_clear()

    @coroutine
    def to_json(self, *fields, **kwargs):
        print 'JON1', fields
        x = self._data.to_json()
        print 'JON2', x
        # document = kwargs.pop('document', None)
        # data = {}
        #
        # fields = set(itertools.chain(*[self.roles[i] for i in args]))
        # for k1 in fields:
        #     k2 = self.aliases.get(k1, k1)
        #     if k2 == '_id':
        #         v = document.id if document else None
        #     elif document and hasattr(document, k2):
        #         print 'M1', k1, k2
        #         v = getattr(document, k2)
        #         if is_future(v):
        #             v = yield v
        #     elif hasattr(self, k2):
        #         print 'M2', k1, k2
        #         v = getattr(document, k2)
        #         if is_future(v):
        #             v = yield v
        #     else:
        #         v = self._data[k2].to_json(**kwargs)
        #     data[k1] = v
        # raise Return(data)


    #     for i in field_data:
    #         if i['attr']:
    #             v = getattr(self, i['field'])
    #             if is_future(v):
    #                 v = yield v
    #         else:
    #             yield self.preload(i['field'], cache=cache)
    #             try:
    #                 v = self._data[i['field']]
    #             except (ValueError, AttributeError):
    #                 v = None

    #         if isinstance(v, Node):
    #             v = v.value()
    #         if v is not None:
    #             if isinstance(v, ObjectId):
    #                 v = str(v)
    #             elif isinstance(v, Document):
    #                 v = yield v.to_json(cache=cache)
    #         data[i['alias']] = v
    #     raise Return(data)

    def from_json(self):
        pass
