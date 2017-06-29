from .manage import ModelManager
from .collections import DictField


class ModelMeta(type):
    def __new__(mcs, name, bases, attr):
        scheme = attr.get('scheme')
        if scheme is not None and not isinstance(scheme, dict):
            attr['scheme'] = getattr(scheme, 'scheme')

        _cls = type.__new__(mcs, name, bases, attr)
        if name != 'Model' and name != 'Document':
            ModelManager.add(_cls)
        return _cls


class Model(DictField, metaclass=ModelMeta):
    scheme = {}

    def __init__(self, data=None, **kwargs):
        super().__init__(self.scheme, **kwargs)
        if data:
            self.set_value(data, **kwargs)

    # def get(self, key=None, **kwargs):
    #     if isinstance(key, (list, tuple)):
    #         data = {}
    #         fields = []
    #         for i in key:
    #             if hasattr(self, i):
    #                 data[i] = getattr(self, i)
    #             else:
    #                 fields.append(i)
    #         return dict(super(Model, self).get(fields, **kwargs), **data)
    #
    #     return super(Model, self).get(key, **kwargs)
