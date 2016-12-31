# coding: utf-8

try:
    import ujson as json
except ImportError:
    import json

from manage import ModelManager


class ModelMeta(type):
    def __new__(mcs, name, bases, attr):
        fields = attr.get('fields')
        if fields is not None and not isinstance(fields, dict):
            attr['fields'] = getattr(fields, 'fields')

        _cls = type.__new__(mcs, name, bases, attr)
        if name != 'Model' and name != 'Document':
            ModelManager.add(_cls)
        return _cls


class Model(object):
    __metaclass__ = ModelMeta
    fields = {}

    def __init__(self, data=None, **kwargs):
        from fields import make_field
        self._parent = kwargs.pop('_parent', None)
        self._val = make_field(self.fields, _parent=self)
        if data:
            assert isinstance(data, dict)
            self._val.set(data, **kwargs)

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._val.value)

    def __getitem__(self, key):
        return self._val.__getitem__(key)

    def __setitem__(self, key, value):
        self._val.setitem(key, value)

    def __delitem__(self, key):
        self._val.__delitem__(key)

    def setitem(self, key, value, **kwargs):
        self._val.setitem(key, value, **kwargs)

    def get(self, *fields, **kwargs):
        data = {}
        _fields = []
        if fields:
            for i in fields:
                if hasattr(self, i):
                    data[i] = getattr(self, i)
                else:
                    _fields.append(i)

        return dict(self._val.get(*_fields, **kwargs), **data)

    def set(self, value, **kwargs):
        self._val.set(value, **kwargs)

    @property
    def value(self):
        return self._val.value

    @property
    def self_value(self):
        return self._val.self_value

    @property
    def dirty(self):
        return self._val.dirty

    @property
    def query(self):
        return self._val.query

    def clear(self):
        self._val.clear()

    def dirty_clear(self):
        self._val.dirty_clear()
