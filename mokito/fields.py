import datetime
try:
    import ujson as json
except ImportError:
    import json

import pytz
from bson import ObjectId
from dateutil.parser import parse

from .errors import MokitoChoiceError
from .tools import SEPARATOR


class Field(object):
    def __init__(self, _default=None, _parent=None, **kwargs):
        self._val = None
        self._parent = _parent
        self._dirty = False
        self._default = _default
        if _default is not None:
            self.set_value(_default)

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.value)

    @property
    def parent(self):
        return self._parent

    def get_dirty(self):
        return self._dirty

    def set_dirty(self, value):
        self._dirty = value

    dirty = property(get_dirty, set_dirty)

    def dirty_clear(self):
        self.dirty = False

    def clear(self):
        self._val = self._default
        self.dirty = True

    def get_value(self, **kwargs):
        return self._val

    def set_value(self, value, **kwargs):
        res = self._val != value
        if res:
            self._val = value
            self.dirty = True

    value = property(get_value, set_value)

    @property
    def self_value(self):
        return self._val


class AnyField(Field):
    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        try:
            if isinstance(self._val, (list, tuple)):
                k1 = int(k1)
            item = self._val[k1]
        except KeyError:
            item = AnyField(_parent=self)
        if k2:
            item = item.__getitem__(k2)

        return item if isinstance(item, Field) else AnyField(item)

    def set_value(self, value, **kwargs):
        if isinstance(value, tuple):
            value = list(value)
        super().set_value(value, **kwargs)

    value = property(Field.get_value, set_value)


class NumberField(Field):
    def __iadd__(self, other):
        if isinstance(other, Field):
            other = other.get_value()
        return (self._val or 0) + other


class IntField(NumberField):
    def set_value(self, value, **kwargs):
        if value is not None:
            value = int(value)
        super().set_value(value, **kwargs)

    value = property(NumberField.get_value, set_value)


class FloatField(NumberField):
    def set_value(self, value, **kwargs):
        if value is not None:
            value = float(value)
        super().set_value(value, **kwargs)

    value = property(NumberField.get_value, set_value)


class StringField(Field):
    def set_value(self, value, **kwargs):
        if value is not None:
            if isinstance(value, (bytes, bytearray)):
                value = str(value, 'utf-8')
            elif not isinstance(value, str):
                value = str(value)
        super().set_value(value, **kwargs)

    value = property(Field.get_value, set_value)


class BooleanField(Field):
    def set_value(self, value, **kwargs):
        if value is not None:
            value = bool(value)
        super().set_value(value, **kwargs)

    value = property(Field.get_value, set_value)


class ObjectIdField(Field):
    def get_value(self, _format=None, **kwargs):
        if self._val is not None:
            return str(self._val) if _format == 'json' else self._val

    def set_value(self, value, **kwargs):
        if value is not None:
            value = ObjectId(value)
        super().set_value(value, **kwargs)

    value = property(get_value, set_value)


class DateTimeField(Field):
    def get_value(self, _date_format=None, tz_name=None, without_microsecond=True, tz=None, **kwargs):
        if _date_format is None and (tz_name or tz):
            _date_format = 'iso'
        if self._val is None or _date_format is None:
            return self._val

        _tz = pytz.timezone(tz_name) if tz_name else tz
        val = _tz.fromutc(self._val) if _tz else self._val
        if without_microsecond:
            val = val.replace(microsecond=0)

        return val.isoformat() if _date_format.lower() == 'iso' else val.strftime(_date_format)

    def set_value(self, value, _date_format=None, **kwargs):
        if not (value is None or isinstance(value, datetime.datetime)):
            if _date_format and _date_format != 'iso':
                value = datetime.datetime.strptime(value, _date_format)
            else:
                try:
                    value = parse(value).replace(tzinfo=None)
                except TypeError:
                    value = None
        super().set_value(value, **kwargs)

    value = property(get_value, set_value)


class ChoiceField(Field):
    def __init__(self, choices, **kwargs):
        """
        :param choices: {mongo_value: orm_value} or [mongo_value] or (mongo_value,)
        :param kwargs:
        """
        super().__init__(**kwargs)
        if isinstance(choices, dict):
            self._choices = choices
        elif isinstance(choices, (list, tuple)):
            self._choices = {i: i for i in choices}
        else:
            raise TypeError()

    def _py_2_mongo(self, value):
        for k, v in self._choices.items():
            if value == v:
                return k

        if value is not None:
            raise MokitoChoiceError(value)

    def get_value(self, inner=False, **kwargs):
        return self._val if inner else self._choices.get(self._val, None)

    def set_value(self, value, inner=False, **kwargs):
        if not inner:
            value = self._py_2_mongo(value)
        super().set_value(value, **kwargs)

    value = property(get_value, set_value)
