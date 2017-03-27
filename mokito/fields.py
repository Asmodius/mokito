# coding: utf-8

import copy
import inspect
import datetime
try:
    import ujson as json
except ImportError:
    import json

import pytz
from bson import ObjectId
from dateutil.parser import parse

from errors import MokitoDBREFError, MokitoChoiceError
from tools import SEPARATOR


def make_field(rules, _parent=None):
    from orm import Model
    if rules is None:
        return NoneField(_parent=_parent)

    elif isinstance(rules, Field):
        x = copy.deepcopy(rules)
        x._parent = _parent
        return x

    else:
        if inspect.isclass(rules):
            _type = rules
            _val = None
        else:
            _type = type(rules)
            _val = rules

        if _type is int:
            return IntField(_default=_val, _parent=_parent)
        if _type is float:
            return FloatField(_default=_val, _parent=_parent)
        if _type is str or _type is unicode:
            return StringField(_default=_val, _parent=_parent)
        if _type is bool:
            return BooleanField(_default=_val, _parent=_parent)
        if _type is ObjectId:
            return ObjectIdField(_default=_val, _parent=_parent)
        if _type is datetime.datetime:
            return DateTimeField(_default=_val, _parent=_parent)

        if _type is list:
            return ListField(rules, _parent=_parent)
        if _type is tuple:
            return TupleField(rules, _parent=_parent)
        if _type is dict:
            return DictField(rules, _parent=_parent)

        if issubclass(_type, Model):
            return _type(_parent=_parent)

        if issubclass(_type, Field):
            x = _type(rules)
            x._parent = _parent
            return x
        raise TypeError()


class Field(object):

    def __init__(self, _default=None, _parent=None, **kwargs):
        self._val = None
        self._parent = _parent
        self._dirty = False
        self._default = _default
        if _default is not None:
            self.set(_default)

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.value)

    @property
    def parent(self):
        return self._parent

    @property
    def dirty(self):
        return self._dirty

    def dirty_clear(self):
        self._dirty = False

    def _value(self):
        return self._val

    def set(self, value, **kwargs):
        res = self._val != value
        if res:
            self._val = value
            self._dirty = True

    value = property(_value, set)

    def get(self, **kwargs):
        return self._value()

    @property
    def self_value(self):
        return self._val

    def clear(self):
        self._val = self._default
        self._dirty = True


class UndefinedField(Field):
    def __getitem__(self, key):
        raise IndexError(key)

    def __setitem__(self, key, value):
        raise IndexError(key)

    def __delitem__(self, key):
        raise IndexError(key)

    def _value(self):
        return

    def set(self, value, **kwargs):
        pass

    value = property(_value, set)


class NoneField(Field):
    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        try:
            if isinstance(self._val, (list, tuple)):
                k1 = int(k1)
            ret = self._val[k1]
        except KeyError:
            ret = UndefinedField(_parent=self)
        if k2:
            ret = ret.__getitem__(k2)

        return ret if isinstance(ret, Field) else NoneField(ret)

    def set(self, value, **kwargs):
        if isinstance(value, tuple):
            value = list(value)
        super(NoneField, self).set(value, **kwargs)

    value = property(Field._value, set)


class NumberField(Field):
    def __iadd__(self, other):
        if isinstance(other, Field):
            other = other.value
        return (self._val or 0) + other


class IntField(NumberField):
    def set(self, value, **kwargs):
        if value is not None:
            value = int(value)
        super(IntField, self).set(value, **kwargs)

    value = property(NumberField._value, set)


class FloatField(NumberField):
    def set(self, value, **kwargs):
        if value is not None:
            value = float(value)
        super(FloatField, self).set(value, **kwargs)

    value = property(NumberField._value, set)


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

    value = property(Field._value, set)


class BooleanField(Field):
    def set(self, value, **kwargs):
        if value is not None:
            value = bool(value)
        super(BooleanField, self).set(value, **kwargs)

    value = property(Field._value, set)


class ObjectIdField(Field):
    def get(self, _format=None, **kwargs):
        if self._val is not None:
            return str(self._val) if _format == 'json' else self._val

    def set(self, value, **kwargs):
        if value is not None:
            value = ObjectId(value)
        super(ObjectIdField, self).set(value, **kwargs)

    value = property(Field._value, set)


class DateTimeField(Field):
    def get(self, _date_format=None, tz_name=None, without_microsecond=True, tz=None, **kwargs):
        if _date_format is None and (tz_name or tz):
            _date_format = 'iso'
        if self._val is None or _date_format is None:
            return self._val

        _tz = pytz.timezone(tz_name) if tz_name else tz
        val = _tz.fromutc(self._val) if _tz else self._val
        if without_microsecond:
            val = val.replace(microsecond=0)

        return val.isoformat() if _date_format.lower() == 'iso' else val.strftime(_date_format)

    def set(self, value, _date_format=None, **kwargs):
        if not (value is None or isinstance(value, datetime.datetime)):
            if _date_format and _date_format != 'iso':
                value = datetime.datetime.strptime(value, _date_format)
            else:
                try:
                    value = parse(value).replace(tzinfo=None)
                except TypeError:
                    value = None
        super(DateTimeField, self).set(value, **kwargs)

    value = property(Field._value, set)


class ChoiceField(Field):
    def __init__(self, choices, **kwargs):
        """
        :param choices: {mongo_value: orm_value} or [mongo_value] or (mongo_value,)
        :param kwargs:
        """
        super(ChoiceField, self).__init__(**kwargs)
        if isinstance(choices, dict):
            self._choices = choices
        elif isinstance(choices, (list, tuple)):
            self._choices = {i: i for i in choices}
        else:
            raise TypeError()

    def _orm_2_mongo(self, value):
        for k, v in self._choices.items():
            if value == v:
                return k

        if value is not None:
            raise MokitoChoiceError(value)

    def get(self, inner=False, **kwargs):
        return self._val if inner else self._choices.get(self._val, None)

    def _value(self):
        return self._choices.get(self._val, None)

    def set(self, value, inner=False, **kwargs):
        if not inner:
            value = self._orm_2_mongo(value)
        super(ChoiceField, self).set(value, **kwargs)

    value = property(_value, set)


class CollectionField(Field):

    def __init__(self, _parent=None, **kwargs):
        super(CollectionField, self).__init__(_parent=_parent, **kwargs)
        self._add_docs = set()  # added Document()
        self._del_docs = set()  # deleted Document()

    def __getitem__(self, key):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        self.setitem(key, value)

    def setitem(self, key, value, **kwargs):
        raise NotImplementedError

    def set(self, value, **kwargs):
        if value is None:
            self.clear()

        elif isinstance(value, dict):
            for k, v in value.items():
                self.setitem(k, v, **kwargs)

        else:
            raise TypeError()

    def dirty_clear(self):
        from orm import Document
        self._dirty = False
        self._add_docs = set()
        self._del_docs = set()
        for i in self._val.values():
            if not isinstance(i, Document):
                i.dirty_clear()

    @property
    def dirty(self):
        if not self._dirty:
            self._dirty = any(i.dirty for i in self._val.values())
        return self._dirty


class ArrayField(CollectionField):
    def __getitem__(self, key):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __len__(self):
        return max(map(int, self._val.keys())) + 1 if self._val else 0

    def __iter__(self):
        for i in range(len(self)):
            yield self.__getitem__(i)

    def setitem(self, key, value, **kwargs):
        raise NotImplementedError

    def get(self, key=None, **kwargs):
        if not (isinstance(key, (list, tuple)) or key is None):
            key = [key]
        return [self.__getitem__(i).get(**kwargs) for i in key or range(len(self))]

    def set(self, value, **kwargs):
        if isinstance(value, (list, tuple)):
            value = {str(k): v for k, v in enumerate(value)}
        super(ArrayField, self).set(value, **kwargs)

    def _value(self):
        return [self._val[i].value if i in self._val else None for i in map(str, range(len(self)))]

    value = property(_value, set)

    @property
    def self_value(self):
        return [self._val[i].self_value if i in self._val else None for i in map(str, range(len(self)))]

    def _set(self, k1, k2, value, **kwargs):
        from orm import Document, Model
        try:
            x = self._val[k1]
        except KeyError:
            raise IndexError(k1)
        if k2:
            x.setitem(k2, value, **kwargs)
        else:
            # if isinstance(value, Model):
            #     value = value.value

            if isinstance(x, Document):
                if value is None:
                    self._del_docs.add(k1)
                    self._add_docs.discard(k1)
                    del self._val[k1]
                elif isinstance(value, Document):
                    self._del_docs.discard(k1)
                    self._add_docs.add(k1)
                    self._val[k1] = value
                    if x.id != value.id:
                        self._dirty = True
                else:
                    self._del_docs.discard(k1)
                    self._add_docs.add(k1)
                    x.set(value, **kwargs)
            else:
                if isinstance(value, Model):
                    value = value.value

                x.set(value, **kwargs)

    @property
    def query(self):
        from orm import Document
        ret = {"$set": []}
        for k in range(len(self)):
            k = str(k)
            v = self._val.get(k)

            if k in self._add_docs:
                # if v._id is None or v.query:
                if getattr(v, '_id') is None or v.query:
                    raise MokitoDBREFError(v)
                ret["$set"].append(v.dbref)

            elif k in self._del_docs:
                ret["$set"].append(None)

            elif self.dirty:
                if v is None:
                    ret["$set"].append(None)

                elif isinstance(v, Document):
                    # if v._id is None or v.query:
                    if getattr(v, '_id') is None or v.query:
                        raise MokitoDBREFError(v)
                    ret["$set"].append(v.dbref)

                else:
                    # ret["$set"].append(v.value)
                    ret["$set"].append(v.get(inner=True))

        if not (ret["$set"] or self.dirty):
            del ret["$set"]
        return ret


class ListField(ArrayField):
    def __init__(self, rules, _parent=None, **kwargs):
        super(ListField, self).__init__(_parent=_parent, **kwargs)
        self._val = {}

        if not rules:
            rules = [None]

        # self._rules = make_field((rules+[None])[0], _parent=self)

        _rules = [make_field(i, _parent=self) for i in rules]
        # self._rules = _rules[0]
        self._rules = copy.deepcopy(_rules[0])
        for k, v in enumerate(_rules):
            if v._default:
                v._parent = self
                self._val[str(k)] = v

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        try:
            ret = self._val[k1]
        except KeyError:
            ret = UndefinedField(_parent=self)
        return ret.__getitem__(k2) if k2 else ret

    def setitem(self, key, value, **kwargs):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if not k1.isdigit():
            raise TypeError('%s is not integer' % k1)
        if k1 not in self._val:
            x = copy.deepcopy(self._rules)
            x._parent = self
            self._val[k1] = x
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
        # self._dirty = True

    def pop(self, key=-1):
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
            ret = UndefinedField(_parent=self)
        return ret


class TupleField(ArrayField):

    def __init__(self, rules, _parent=None, **kwargs):
        super(TupleField, self).__init__(_parent=_parent, **kwargs)
        self._val = {str(k): make_field(v, _parent=self) for k, v in enumerate(rules)}

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        try:
            ret = self._val[k1]
            return ret.__getitem__(k2) if k2 else ret
        except (KeyError, AttributeError):
            raise IndexError(key)

    def __delitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        try:
            x = self._val[k1]
        except KeyError:
            raise IndexError
        if k2:
            x.__delitem__(k2)
        else:
            x.set(None)
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

    def __init__(self, rules, _parent=None, **kwargs):
        super(DictField, self).__init__(_parent=_parent, **kwargs)
        self._rules = bool(rules)
        if rules:
            self._val = {k: make_field(v, _parent=self) for k, v in rules.items()}
        else:
            self._val = {}

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        try:
            ret = self._val[k1]
        except KeyError:
            ret = UndefinedField(_parent=self)
        return ret.__getitem__(k2) if k2 else ret

    def setitem(self, key, value, **kwargs):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if self._rules:
            self._set(k1, k2, value, **kwargs)
        else:
            self._val[k1] = make_field(value, _parent=self)
            # raise NotImplementedError

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
        from orm import Document, Model
        try:
            x = self._val[k1]
        except KeyError:
            return
        if k2:
            x.setitem(k2, value, **kwargs)
        else:
            # if isinstance(value, Model):
            #     value = value.value

            if isinstance(x, Document):
                if value is None:
                    self._del_docs.add(k1)
                    self._add_docs.discard(k1)
                    del self[k1]
                elif isinstance(value, Document):
                    self._del_docs.discard(k1)
                    self._add_docs.add(k1)
                    self._val[k1] = value
                    if x.id != value.id:
                        self._dirty = True
                else:
                    self._del_docs.discard(k1)
                    self._add_docs.add(k1)
                    x.set(value, **kwargs)
            else:
                if isinstance(value, Model):
                    value = value.value

                x.set(value, **kwargs)

    def get(self, key=None, **kwargs):
        if key is None:
            key = self._val.keys()
        if isinstance(key, (list, tuple)):
            return {i: self.__getitem__(i).get(**kwargs) for i in key}
        return self.__getitem__(key).get(**kwargs)

    def _value(self):
        return {k: v.value for k, v in self._val.items()}

    value = property(_value, CollectionField.set)

    @property
    def self_value(self):
        return {k: v.self_value for k, v in self._val.items()}

    def items(self):
        return self._val.items()

    def clear(self):
        if self._rules:
            for i in self._val.values():
                i.clear()
        else:
            self._val = {}
        self._dirty = True

    @property
    def query(self):
        from orm import Model, Document
        ret = {"$set": {}, "$unset": {}}

        if not self._rules:
            ret['$set'] = self.get(inner=True)

        else:
            for k, v in self._val.items():
                if k in self._add_docs:
                    # if v._id is None or v.query:
                    if getattr(v, '_id') is None or v.query:
                        raise MokitoDBREFError(v)
                    ret["$set"][k] = v.dbref

                elif k in self._del_docs:
                    ret["$unset"][k] = ''

                elif v.dirty and not isinstance(v, Document):
                    if isinstance(v, Model):
                        _q = v.query
                        for j in ["$set", "$unset"]:
                            if j in _q:
                                for k1, v1 in _q[j].items():
                                    ret[j]["%s.%s" % (k, k1)] = v1

                    elif isinstance(v, ArrayField):
                        _q = v.query
                        if "$set" in _q:
                            ret["$set"][k] = _q["$set"]

                    elif isinstance(v, DictField):
                        _q = v.query
                        for j in ["$set", "$unset"]:
                            if j in _q:
                                if v._rules:
                                    for k1, v1 in _q[j].items():
                                        ret[j]["%s.%s" % (k, k1)] = v1
                                else:
                                    ret[j][k] = _q[j]

                    else:
                        ret['$set'][k] = v.value

        if not ret["$set"]:
            del ret["$set"]
        if not ret["$unset"]:
            del ret["$unset"]
        return ret
