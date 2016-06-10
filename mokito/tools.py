# coding: utf-8

from pymongo import ASCENDING, DESCENDING


def fields2sort(sort):
    if isinstance(sort, basestring):
        sort = [sort]
    return [(i[1:], DESCENDING,) if i[0] == '-' else
            (i, ASCENDING,) if isinstance(i, basestring) else
            i for i in sort]
