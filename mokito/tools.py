# coding: utf-8

import six
from pymongo import ASCENDING, DESCENDING


SEPARATOR = '.'


def fields2sort(sort):
    if isinstance(sort, basestring):
        sort = [sort]
    return [(i[1:], DESCENDING,) if i[0] == '-' else
            (i, ASCENDING,) if isinstance(i, basestring) else
            i for i in sort]


class _MetaKnownClasses(type):
    def __contains__(cls, key):
        return (key in cls.data) or (key in cls.data.values())


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
