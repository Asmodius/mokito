# coding: utf-8

import six


class _MetaKnownClasses(type):
    def __contains__(cls, key):
        return (key in cls.data) or (key in cls.data.values())

    def __getitem__(self, arg):
        return self.get(arg)


@six.add_metaclass(_MetaKnownClasses)
class KnownClasses(object):
    data = {}

    @classmethod
    def add(cls, _class):
        name = _class.__module__ + '.' + _class.__name__
        cls.data[name] = _class

    @classmethod
    def get(cls, _class):
        if isinstance(_class, six.string_types):
            return cls.data.get(_class)
        return _class
