# coding: utf-8

SEPARATOR = '.'


class DValue(object):

    def __init__(self):
        self._data = {}

    def __repr__(self):
        return '%s%s' % (self.__class__.__name__, self._data)

    def __setitem__(self, key, value):
        if not (key in self._data and self._data[key] == value):
            self._data[key] = value
            return True

    def __getitem__(self, key):
        return self._data.get(key)

    def __contains__(self, item):
        return item in self._data

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

# #     def copy(self):
# #         return self.__class__(self._data)


class AValue(DValue):

    def __init__(self):
        super(AValue, self).__init__()
        self._max_item = -1

    def __repr__(self):
        return '%s%s' % (self.__class__.__name__, self[:])

#     def __len__(self):
#         return self._max_item + 1

#     def append(self, value):
#         self._max_item += 1
#         self._data[self._max_item] = value

    def __setitem__(self, key, value):
        key = int(key)
        self._max_item = max(self._max_item, key)
        return super(AValue, self).__setitem__(key, value)

    def __getitem__(self, key):
        return self._data.get(int(key))

    def __getslice__(self, start, stop):
        start = max(start, 0)
        stop = min(max(stop, 0), self._max_item + 1)
        return [self._data.get(i) for i in xrange(start, stop)]

    def keys(self):
        return range(self._max_item + 1)

#     def __len__(self):
#         return self._max_item + 1
#
#     def __add__(self, other):
#         if isinstance(other, AValue):
#             return self.__class__(self[:] + other[:])
#         else:
#             return self.__class__(self[:] + list(other))
#
# #     def update(self, data):
# #         if isinstance(data, AValue):
# #             self.update(data._data)
# #         elif isinstance(data, (list, tuple)):
# #             for k, v in enumerate(data):
# #                 self[k] = v
# #         elif isinstance(data, dict):
# #             for k, v in data.items():
# #                 k = int(k)
# #                 self[k] = v
# #         elif data is not None:
# #             self.update([data])


class DM(object):

    def __init__(self):
        """
        :param fields:
            - None # Untyped field
            - bool
            - int
            - float
            - long
            - str
            - unicode
            - dict
            - list
            - tuple
            - bson.ObjectId
            - datetime.datetime

            # - bson.binary.Binary
            # - bson.DBRef
            # - bson.Code
            # - type(re.compile(""))
            # - uuid.UUID
            # - CustomType
        """
        self._val = None
        self._dirty = set()

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._val)

    def __setitem__(self, key, value):
        key = str(key)
        k, _, v = key.partition(SEPARATOR)

        if self._field_exist(k):
            if v:
                dirty = self._val[k].__setitem__(v, value)

            else:
                data_type = self._get_data_type(k)
                value = self._convert(data_type, value)
                dirty = self._val.__setitem__(k, value) or isinstance(value, DM)

            if dirty:
                self._dirty.add(k)
                return True

    def dirty(self):
        for k in set(self._rules.keys()) - self._dirty:
            v = self._val[k]
            if isinstance(v, DM) and v.dirty():
                self._dirty.add(k)
        return self._dirty

    def dirty_clear(self):
        self._dirty.clear()
        for i in self._rules.keys():
            v = self._val[i]
            if isinstance(v, DM):
                v.dirty_clear()

    def dirty_data(self):
        return self._dirty_data(None)

    def _dirty_data(self, prefix):
        dirty = self.dirty()
        result = {}
        for k in dirty:
            v = self._val[k]
            if isinstance(v, DM):
                result.update(v._dirty_data(k))
            else:
                key = '%s.%s' % (prefix, k) if prefix else k
                result[key] = v
        return result

    @staticmethod
    def _convert(data_type, value):
        if isinstance(data_type, dict):
            return DM_dict(data_type, value)

        elif isinstance(data_type, list):
            return DM_list(data_type, value)

        elif isinstance(data_type, tuple):
            return DM_tuple(data_type, value)

        elif not (None in (data_type, value) or isinstance(value, data_type)):
            try:
                return data_type(value)
            except ValueError:
                pass
        return value


class DM_list(DM):

    def __init__(self, fields, data=None):
        DM.__init__(self)
        self._rules = {k: v for k, v in enumerate(fields)}
        self._val = AValue()

        _data = data or []
        data_type = self._get_data_type(0)
        for k, value in enumerate(_data):
            self._val[k] = self._convert(data_type, value)

    def _field_exist(self, key):
        return True

    def _get_data_type(self, key):
        return self._rules[0]

#     def __getitem__(self, key):
#         return self._val[int(key)]
#
#     def __getslice__(self, start, stop):
#         start = max(start, 0)
#         stop = min(stop, len(self._val))
#         return [self[i] for i in xrange(start, stop)]

    def inner_data(self, fields=None):
        res = []
        if not fields:
            fields = self._rules.keys()
            #fields = self._val.keys()

        for key in fields:
            key = str(key)
            k, _, v = key.partition(SEPARATOR)
            value = self._val[k]

            print 'INN-0', k, v
            print 'INN-1', value

#             if isinstance(value, DM_dict):
#                 res.setdefault(k, {})
#                 print 'INN-2', value
#                 value = value.inner_data([v] if v else None)
#                 res[k].update(value)
#
#             elif isinstance(value, DM_list):
#                 res.setdefault(k, [])
#                 print 'INN-3', value
#                 value = value.inner_data([v] if v else None)
#                 print 'INN-4', value
#                 res[k].extend(value)
#
#             else:
#                 res[k] = value

        return res


class DM_tuple(DM_list):

    def __init__(self, fields, data=None):
        DM.__init__(self)
        self._rules = {k: v for k, v in enumerate(fields)}
        self._val = AValue()

        l = len(self._rules)
        _data = ((list(data) if data else []) + ([None] * l))[:l]
        for k, value in enumerate(_data):
            data_type = self._get_data_type(k)
            self._val[k] = self._convert(data_type, value)

    def _get_data_type(self, key):
        return self._rules[int(key)]


class DM_dict(DM):

    def __init__(self, fields, data=None):
        DM.__init__(self)
        self._rules = fields
        self._val = DValue()

        _data = data or {}
        for k, data_type in self._rules.items():
            value = _data.get(k)
            self._val[k] = self._convert(data_type, value)

    def _field_exist(self, key):
        return not self._rules or key in self._rules

    def _get_data_type(self, key):
        return self._rules.get(key)

    def __getitem__(self, key):
        k, _, v = key.partition(SEPARATOR)
        if k in self._rules.keys():
            res = self._val[k]
            if res is not None and v:
                res = res[v]
            return res

    def inner_data(self, fields=None):
        res = {}
        if not fields:
            #fields = self._rules.keys()
            fields = self._val.keys()

        for key in fields:
            key = str(key)
            k, _, v = key.partition(SEPARATOR)
            value = self._val[k]

            if isinstance(value, DM_dict):
                res.setdefault(k, {})
                value = value.inner_data([v] if v else None)
                res[k].update(value)

            elif isinstance(value, DM_list):
                res.setdefault(k, [])
                value = value.inner_data([v] if v else None)
                res[k].extend(value)

            else:
                res[k] = value

        return res
