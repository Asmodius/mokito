import copy
import inspect
import datetime

from bson import ObjectId
# from pymongo import ASCENDING, DESCENDING


SEPARATOR = '.'


def make_field(rules, _parent=None):
    from .models import Model
    # from .documents import Document
    from .fields import Field, AnyField, IntField, FloatField, StringField, BooleanField, ObjectIdField, DateTimeField
    from .collections import ListField, TupleField, DictField
    from .geo_fileds import GEOField, _Point1, _Point2

    if rules is None:
        return AnyField(_parent=_parent)

    elif isinstance(rules, Field):
        x = copy.deepcopy(rules)
        x._parent = _parent
        return x

    else:
        if inspect.isclass(rules):
            # print('l0-1')
            _type = rules
            _val = None
        else:
            # print('l0-2')
            _type = type(rules)
            _val = rules

        if _type is int:
            return IntField(_val, _parent=_parent)
        if _type is float:
            return FloatField(_val, _parent=_parent)
        if _type is str:
            return StringField(_val, _parent=_parent)
        if _type is bool:
            return BooleanField(_val, _parent=_parent)
        if _type is ObjectId:
            return ObjectIdField(_val, _parent=_parent)
        if _type is datetime.datetime:
            return DateTimeField(_val, _parent=_parent)

        if _type is list:
            # print('L1', rules, _val) # rules == _val - может rules поменять на _val ?
            return ListField(rules, _parent=_parent)
        if _type is tuple:
            return TupleField(rules, _parent=_parent)
        if _type is dict:
            return DictField(rules, _parent=_parent)

        # if issubclass(_type, Document):
        #     print('SC', _type)
        #     return _type(_parent=_parent)

        if issubclass(_type, _Point1):
            return _type(_parent=_parent)

        if issubclass(_type, _Point2):
            return _type(_parent=_parent)

        if issubclass(_type, GEOField):
            return _type(_parent=_parent)

        if issubclass(_type, Model):
            return _type(_parent=_parent)

        if issubclass(_type, Field):
            return _type(_parent=_parent)
            # x = _type(rules)
            # x._parent = _parent
            # return x
        raise TypeError()


# def fields2sort(sort):
#     if isinstance(sort, basestring):
#         sort = [sort]
#     return [(i[1:], DESCENDING,) if i[0] == '-' else
#             (i, ASCENDING,) if isinstance(i, basestring) else
#             i for i in sort]


# def norm_spec(spec):
#     if spec is None:
#         return {}
#
#     if isinstance(spec, basestring):
#         return {"_id": ObjectId(spec)}
#
#     if isinstance(spec, ObjectId):
#         return {"_id": spec}
#
#     return spec
