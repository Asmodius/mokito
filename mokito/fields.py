# coding: utf-8

import copy
import inspect
import datetime
from collections import OrderedDict
try:
    import ujson as json
except ImportError:
    import json

import pytz
from bson import ObjectId, DBRef
from dateutil.parser import parse

from errors import MokitoDBREFError, MokitoChoiceError
from orm import Document
from model import Model
from tools import SEPARATOR


class Field(object):
    def __init__(self, *args, **kwargs):
        self._val = None
        self._dirty = False

    @property
    def dirty(self):
        return self._dirty

    def dirty_clear(self):
        self._dirty = False

    def get(self, **kwargs):
        return self._val

    def set(self, value, **kwargs):
        res = self._val != value
        if res:
            self._val = value
            self._dirty = True

    @property
    def value(self):
        return self._val

    @classmethod
    def make(cls, rules=None):
        if rules is None:
            return Field()
        elif isinstance(rules, Field):
            return copy.deepcopy(rules)
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
            if issubclass(_type, Field):
                return _type(rules)
            raise TypeError()

    def clear(self):
        self._val = None
        self._dirty = True

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.value)


class IntField(Field):
    def set(self, value, **kwargs):
        if value is not None:
            value = int(value)
        super(IntField, self).set(value, **kwargs)


class FloatField(Field):
    def set(self, value, **kwargs):
        if value is not None:
            value = float(value)
        super(FloatField, self).set(value, **kwargs)


class StringField(Field):
    def __getitem__(self, key):
        return self._val[int(key)]

    def set(self, value, **kwargs):
        if value is not None:
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            else:
                value = str(value)
        super(StringField, self).set(value, **kwargs)


class BooleanField(Field):
    def set(self, value, **kwargs):
        if value is not None:
            value = bool(value)
        super(BooleanField, self).set(value, **kwargs)


class ObjectIdField(Field):
    def get(self, as_json=False, **kwargs):
        if self._val is not None:
            return str(self._val) if as_json else self._val

    def set(self, value, **kwargs):
        if value is not None:
            value = ObjectId(value)
        super(ObjectIdField, self).set(value, **kwargs)


class DateTimeField(Field):
    def get(self, date_format=None, tz_name=None, without_microsecond=True, tz=None, **kwargs):
        if date_format is None and (tz_name or tz):
            date_format = 'iso'
        if self._val is None or date_format is None:
            return self._val

        _tz = pytz.timezone(tz_name) if tz_name else tz
        val = _tz.fromutc(self._val) if _tz else self._val
        if without_microsecond:
            val = val.replace(microsecond=0)

        return val.isoformat() if date_format.lower() == 'iso' else val.strftime(date_format)

    def set(self, value, date_format=None, **kwargs):
        if not (value is None or isinstance(value, datetime.datetime)):
            if date_format and date_format != 'iso':
                value = datetime.datetime.strptime(value, date_format)
            else:
                value = parse(value).replace(tzinfo=None)
        super(DateTimeField, self).set(value, **kwargs)


class ChoiceField(Field):
    def __init__(self, choices, **kwargs):
        super(ChoiceField, self).__init__(**kwargs)
        if isinstance(choices, (list, type)):
            choices = {i: i for i in choices}
        self.choices = choices

    def get(self, **kwargs):
        return self.choices.get(self._val, None)

    def set(self, value, inner=False, **kwargs):
        if not inner:
            if value is not None:
                for k, v in self.choices.items():
                    if v == value:
                        value = k
                        break
                else:
                    raise MokitoChoiceError(value)
        super(ChoiceField, self).set(value, **kwargs)


class CollectionField(Field):
    def __init__(self):
        super(CollectionField, self).__init__()
        self._add_docs = set()
        self._del_docs = set()

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        ret = self._val[k1]
        return ret[k2] if k2 else ret

    def __setitem__(self, key, value):
        self.setitem(key, value)

    def setitem(self, key, value, **kwargs):
        raise NotImplemented

    def set(self, value, **kwargs):
        if value is not None:
            key_param, all_param = self._mk_param(**kwargs)
            for k, v in value.items():
                self.setitem(k, v, **dict(key_param.get(k, {}), **all_param))

    def dirty_clear(self):
        self._dirty = False
        self._add_docs = set()
        self._del_docs = set()
        for i in self._val.values():
            i.dirty_clear()

    @staticmethod
    def _mk_param(**kwargs):
        key_param = {}
        all_param = {}
        for k, v in kwargs.items():
            k1, _, k2 = str(k).partition(SEPARATOR)
            if k2:
                try:
                    key_param.setdefault(k1, {})
                    key_param[k1][k2] = v
                except ValueError:
                    all_param[k] = v
            else:
                all_param[k1] = v
        return key_param, all_param

    @property
    def dirty(self):
        if not self._dirty:
            self._dirty = any(i.dirty for i in self._val.values())
        return self._dirty


class ArrayField(CollectionField):
    def __getitem__(self, key):
        try:
            return super(ArrayField, self).__getitem__(str(key))
        except KeyError:
            raise IndexError(key)

    def __len__(self):
        return max(map(int, self._val.keys())) + 1 if self._val else 0

    @property
    def value(self):
        return [self._val[i].value if i in self._val else None for i in map(str, range(len(self)))]

    @property
    def query(self):
        ret = {"$set": [], "$unset": {}}
        # print 'QQ', self._add_docs, self._del_docs
        for k in range(len(self)):
            k = str(k)
            v = self._val.get(k)
            # print 'FD1', k, v
            # print 'FD2', self._val
            if k in self._add_docs:
                if v._id is None or v.query:
                    raise MokitoDBREFError(v)
                ret["$set"].append(v.dbref)

            elif k in self._del_docs:
                ret["$set"].append(None)

            elif self.dirty:
                if v is None:
                    ret["$set"].append(None)
                elif isinstance(v, Document):
                    if v._id is None or v.query:
                        raise MokitoDBREFError(v)
                    ret["$set"].append(v.dbref)
                else:
                    ret["$set"].append(v.value)

        if not (ret["$set"] or self.dirty):
            del ret["$set"]
        if not ret["$unset"]:
            del ret["$unset"]
        return ret

        # return {'$set': self.value} if self.dirty else {}

    def _set(self, k1, k2, value, **kwargs):
        try:
            x = self._val[k1]
        except KeyError:
            raise IndexError(k1)
        if k2:
            x.setitem(k2, value, **kwargs)
        else:
            if isinstance(x, Document):
                if value is None:
                    self._del_docs.add(k1)
                    self._add_docs.discard(k1)
                    del self._val[k1]
                else:
                    self._del_docs.discard(k1)
                    self._add_docs.add(k1)
                    x.set(value, **kwargs)
            else:
                x.set(value, **kwargs)

    def get(self, *fields, **kwargs):
        key_param, all_param = self._mk_param(**kwargs)

        _fields = OrderedDict()
        for k in fields or range(len(self)):
            k1, _, k2 = str(k).partition(SEPARATOR)
            _fields.setdefault(k1, [])
            if k2 and k2 not in _fields[k1]:
                _fields[k1].append(k2)

        ret = []
        for k1, k2 in _fields.items():
            if k1 in self._val:
                x = self._val[k1].get(*k2, **dict(key_param.get(k1, {}), **all_param))
            else:
                x = None
            ret.append(x)
        return ret

    def set(self, value, **kwargs):
        if isinstance(value, (list, tuple)):
            value = {str(k): v for k, v in enumerate(value)}
        super(ArrayField, self).set(value, **kwargs)


class ListField(ArrayField):
    def __init__(self, rules):
        super(ListField, self).__init__()
        self._rules = Field.make((rules+[None])[0])
        self._val = {}

    def setitem(self, key, value, **kwargs):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if not k1.isdigit():
            raise TypeError('%s is not integer' % k1)
        if k1 not in self._val:
            self._val[k1] = copy.deepcopy(self._rules)
        self._set(k1, k2, value, **kwargs)

    def __delitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        try:
            x = self._val[k1]
        except KeyError:
            raise IndexError
        if k2:
            del x[k2]
            self._dirty = True
        else:
            self.pop(int(k1))

    def clear(self):
        self._val = {}
        self._dirty = True

    def append(self, value):
        self.setitem(len(self), value)
        self._dirty = True

    def pop(self, key=-1, default=None):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if k2:
            return self._val[k1].pop(k2)

        k1 = int(k1)
        if k1 < 0:
            k1 += len(self)

        ret = None
        keys = map(int, self._val.keys())
        keys.sort()
        for i in keys:
            if k1 == i:
                ret = self._val[str(i)]
                self._dirty = True
                del self._val[str(i)]
            elif k1 < i:
                self._val[str(i - 1)] = self._val[str(i)]
                self._dirty = True
                del self._val[str(i)]
        if ret is None:
            ret = copy.deepcopy(self._rules)
            ret.set(default)
        return ret


class TupleField(ArrayField):
    def __init__(self, rules):
        super(TupleField, self).__init__()
        self._val = {str(k): Field.make(v) for k, v in enumerate(rules)}

    def __delitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        try:
            x = self._val[k1]
        except KeyError:
            raise IndexError
        if k2:
            del x[k2]
        else:
            x.clear()
        self._dirty = True

    def setitem(self, key, value, **kwargs):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if not k1.isdigit():
            raise TypeError('%s is not integer' % k1)
        self._set(k1, k2, value, **kwargs)

    def clear(self):
        for i in self._val.values():
            i.clear()
        self._dirty = True


class DictField(CollectionField):
    def __init__(self, rules):
        super(DictField, self).__init__()
        self._rules = bool(rules)
        self._val = {k: self.make(v) for k, v in rules.items()} if rules else {}

    def setitem(self, key, value, **kwargs):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if not self._rules:
            self._val[k1] = Field.make(value)
        self._set(k1, k2, value, **kwargs)

    def __delitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if k2:
            del self._val[k1][k2]
        elif not self._rules:
            del self._val[k1]
        else:
            self._val[k1].clear()
        self._dirty = True

    def _set(self, k1, k2, value, **kwargs):
        x = self._val[k1]
        if k2:
            x.setitem(k2, value, **kwargs)
        else:
            if isinstance(x, Document):
                if value is None:
                    self._del_docs.add(k1)
                    self._add_docs.discard(k1)
                    del self[k1]
                else:
                    self._del_docs.discard(k1)
                    self._add_docs.add(k1)
                    x.set(value, **kwargs)
            else:
                x.set(value, **kwargs)

    @property
    def value(self):
        return {k: v.value for k, v in self._val.items()}

    def get(self, *fields, **kwargs):
        key_param, all_param = self._mk_param(**kwargs)

        _fields = {}
        for k in fields or self._val.keys():
            k1, _, k2 = str(k).partition(SEPARATOR)
            _fields.setdefault(k1, [])
            if k2 and k2 not in _fields[k1]:
                _fields[k1].append(k2)

        ret = {}
        for k1, k2 in _fields.items():
            if k1 in self._val:
                x = self._val[k1].get(*k2, **dict(key_param.get(k1, {}), **all_param))
            else:
                x = None
            ret[k1] = x
        return ret

    def clear(self):
        if self._rules:
            for i in self._val.values():
                i.clear()
        else:
            self._val = {}
        self._dirty = True

    @property
    def query(self):
        ret = {"$set": {}, "$unset": {}}

        if not self._rules:
            ret['$set'] = self.value

        else:
            for k, v in self._val.items():
                if k in self._add_docs:
                    if v._id is None or v.query:
                        raise MokitoDBREFError(v)
                    ret["$set"][k] = v.dbref

                elif k in self._del_docs:
                    ret["$unset"][k] = ''

                elif v.dirty:
                    if isinstance(v, ArrayField):
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

                    elif isinstance(v, Document):
                        raise MokitoDBREFError(v)

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
