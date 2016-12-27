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
        from fields import Field
        # self._data = copy.deepcopy(Field.make(self.fields))
        self._data = Field.make(self.fields)
        if data:
            assert isinstance(data, dict)
            self._data.set(data, **kwargs)

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._data.value)

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __setitem__(self, key, value):
        self._data.setitem(key, value)

    def __delitem__(self, key):
        self._data.__delitem__(key)

    def setitem(self, key, value, **kwargs):
        self._data.setitem(key, value, **kwargs)

    def get(self, *fields, **kwargs):
        data = {}
        _fields = []
        if fields:
            for i in fields:
                if hasattr(self, i):
                    data[i] = getattr(self, i)
                else:
                    _fields.append(i)

        return dict(self._data.get(*_fields, **kwargs), **data)

    def set(self, value, **kwargs):
        self._data.set(value, **kwargs)

    @property
    def value(self):
        return self._data.value

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

    # @coroutine
    # def to_json(self, *fields, **kwargs):
    #     print 'JON1', fields
    #     x = self._data.to_json()
    #     print 'JON2', x
    #     # document = kwargs.pop('document', None)
    #     # data = {}
    #     #
    #     # fields = set(itertools.chain(*[self.roles[i] for i in args]))
    #     # for k1 in fields:
    #     #     k2 = self.aliases.get(k1, k1)
    #     #     if k2 == '_id':
    #     #         v = document.id if document else None
    #     #     elif document and hasattr(document, k2):
    #     #         print 'M1', k1, k2
    #     #         v = getattr(document, k2)
    #     #         if is_future(v):
    #     #             v = yield v
    #     #     elif hasattr(self, k2):
    #     #         print 'M2', k1, k2
    #     #         v = getattr(document, k2)
    #     #         if is_future(v):
    #     #             v = yield v
    #     #     else:
    #     #         v = self._data[k2].to_json(**kwargs)
    #     #     data[k1] = v
    #     # raise Return(data)
    #
    #
    # #     for i in field_data:
    # #         if i['attr']:
    # #             v = getattr(self, i['field'])
    # #             if is_future(v):
    # #                 v = yield v
    # #         else:
    # #             yield self.preload(i['field'], cache=cache)
    # #             try:
    # #                 v = self._data[i['field']]
    # #             except (ValueError, AttributeError):
    # #                 v = None
    #
    # #         if isinstance(v, Node):
    # #             v = v.value()
    # #         if v is not None:
    # #             if isinstance(v, ObjectId):
    # #                 v = str(v)
    # #             elif isinstance(v, Document):
    # #                 v = yield v.to_json(cache=cache)
    # #         data[i['alias']] = v
    # #     raise Return(data)
    #
    # def from_json(self):
    #     pass
