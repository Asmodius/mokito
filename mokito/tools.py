# coding: utf-8

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING


SEPARATOR = '.'


def fields2sort(sort):
    if isinstance(sort, basestring):
        sort = [sort]
    return [(i[1:], DESCENDING,) if i[0] == '-' else
            (i, ASCENDING,) if isinstance(i, basestring) else
            i for i in sort]


def norm_spec(spec):
    if spec is None:
        return {}

    if isinstance(spec, basestring):
        return {"_id": ObjectId(spec)}

    if isinstance(spec, ObjectId):
        return {"_id": spec}

    return spec
