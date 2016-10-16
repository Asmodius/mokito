# coding: utf-8

from bson import DBRef

from known_cls import KnownClasses
from tools import SEPARATOR


class Node(object):
    def __init__(self, rules):
        self._changed = False
        self._val = None
        self._been_set = False
        self._rules = self._normalize(rules)

    def __call__(self):
        return self.__class__(self._rules)

    def __cmp__(self, other):
        return cmp(self.value(), self._cast(other))

    def __lt__(self, other):
        return self.value() < self._cast(other)

    def __le__(self, other):
        return self.value() <= self._cast(other)

    def __eq__(self, other):
        return self.value() == self._cast(other)

    def __ne__(self, other):
        return self.value() != self._cast(other)

    def __gt__(self, other):
        return self.value() > self._cast(other)

    def __ge__(self, other):
        return self.value() >= self._cast(other)

    def __iadd__(self, other):
        return self._val + self._cast(other)

    def __isub__(self, other):
        return self._val - self._cast(other)

    def __imul__(self, other):
        return self._val * self._cast(other)

    def __ifloordiv__(self, other):
        return self._val // self._cast(other)

    def __idiv__(self, other):
        return self._val / self._cast(other)

    def __imod__(self, other):
        return self._val % self._cast(other)

    def __ipow__(self, other):
        return self._val ** self._cast(other)

    def __ilshift__(self, other):
        return self._val << self._cast(other)

    def __irshift__(self, other):
        return self._val >> self._cast(other)

    def __iand__(self, other):
        return self._val & self._cast(other)

    def __ior__(self, other):
        return self._val | self._cast(other)

    def __ixor__(self, other):
        return self._val ^ self._cast(other)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.value())

    def __str__(self):
        return str(self.value())

    @staticmethod
    def _cast(other):
        ret = other.value() if isinstance(other, Node) else other
        if isinstance(ret, unicode):
            ret = ret.encode('utf-8')
        return ret

    @staticmethod
    def _normalize(data_type):
        if data_type in (dict, tuple, list):
            return data_type()
        return data_type

    @classmethod
    def make(cls, data_type):
        data_type = cls._normalize(data_type)

        if isinstance(data_type, dict):
            return NodeDict(data_type)
        elif isinstance(data_type, list):
            return NodeList(data_type)
        elif isinstance(data_type, tuple):
            return NodeTuple(data_type)
        elif data_type in KnownClasses:
            return NodeDocument(data_type)
        else:
            return Node(data_type)

    def set(self, value):
        value = self._cast(value)
        if not (None in (self._rules, value) or isinstance(value, self._rules)):
            value = self._rules(value)
        if value != self._val:
            self._val = value
            self._changed = True
            return True

    def clear(self):
        self._changed = False
        self._val = None

    def dirty_clear(self):
        self._changed = False

    def value(self, default=None):
        return default if self._val is None else self._val

    def keys(self):
        return []

    @property
    def dirty(self):
        return self._changed

    @property
    def been_set(self):
        return self._been_set

    @property
    def query(self):
        return {"$set": self._val}


class NodeDocument(Node):
    def __init__(self, rules):
        self._rules_base = KnownClasses[rules]
        self._rules = self._rules_base
        self._val = None
        self._been_set = False

    def set(self, value):
        value = self._cast(value)
        if value is None:
            ret = self._val is not None
            self._been_set = False
            self._val = None
            return ret

        elif isinstance(value, DBRef):
            if value.collection != self._rules.__collection__:
                for i in self._rules_base.__subclasses__():
                    if value.collection == i.__collection__:
                        self._rules = i
                        break
                else:
                    raise ValueError('Wrong collection: %s and %s' %
                                     (value.collection, self._rules.__collection__))
            if not (self._val and self._val.pk == value.id):
                self._val = self._rules(_id=value.id)
                return True

        elif isinstance(value, self._rules_base):
            if value.dbref != self.dbref or value.dirty or self.dirty:
                self._val = value
                self._been_set = True
                return True
            else:
                return False

        elif isinstance(value, dict):
            self._val = self._rules(value)
            self._been_set = True
            return True

        else:
            raise ValueError()

    def __getitem__(self, key):
        if key == '_id' and self._val is not None:
            return self._val.dbref.id
        elif self._been_set:
            return self._val.__getitem__(key)
        raise ValueError('The document is not loaded')

    def __setitem__(self, key, value):
        if self._been_set:
            self._val.__setitem__(key, value)
            return False
        raise ValueError('The document is not loaded')

    def dirty_clear(self):
        if self._been_set and self._val is not None:
            self._val._data.dirty_clear()

    @property
    def dirty(self):
        if self._been_set and self._val is not None:
            return self._val._data.dirty
        return False

    @property
    def query(self):
        if self._val is not None:
            return self._val._data.query
        raise ValueError('The document is not loaded')

    @property
    def dbref(self):
        # TODO: add multi DB
        if self._val is not None:
            return self._val.dbref
        return DBRef(self._rules.__collection__, None)

    def save(self):
        if self._val is not None:
            return self._val.save()
        raise ValueError('The document is not loaded')

    @property
    def pk(self):
        if self._val is not None:
            return self._val.pk

    @property
    def fields(self):
        if self._val is not None:
            return self._val.fields


class NodeComposite(Node):
    def __init__(self, rules):
        super(NodeComposite, self).__init__(rules)
        self._changed = set()
        self._removed = set()
        self._val = {}
        self.clear()

    def __contains__(self, item):
        raise NotImplemented

    def __setitem__(self, key, value):
        raise NotImplemented

    def __getitem__(self, key):
        raise NotImplemented

    def __delitem__(self, key):
        raise NotImplemented

    def _del_sub_item(self, k1, k2):
        if self._val[k1].__delitem__(k2):
            self._inc_changed(k1)
            return True

    def _inc_changed(self, key):
        self._changed.add(key)
        self._removed.discard(key)

    def _dec_changed(self, key):
        self._changed.discard(key)
        self._removed.add(key)

    def clear(self):
        self._val = {}
        self._changed.clear()
        self._removed.clear()

    def dirty_clear(self):
        self._changed.clear()
        self._removed.clear()
        map(lambda i: i.dirty_clear(), self._val.values())

    def insert(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if k2:
            self._val[k1].insert(k2, value)
        raise AttributeError('object has no attribute "insert"')

    def _dirty_keys(self):
        for k, v in self._val.items():
            if not isinstance(v, NodeDocument) and v.dirty:
                self._inc_changed(k)
        return self._changed | self._removed

    def is_dirty(self, *keys):
        return set(keys) & self._dirty_keys()

    @property
    def dirty(self):
        return bool(self._dirty_keys())

    @property
    def query(self):
        raise NotImplemented

    def setdefault(self, key, value):
        old = self.__getitem__(key)
        if old is None or old.value() is None:
            self.__setitem__(key, value)


class NodeArray(NodeComposite):
    def __init__(self, rules):
        super(NodeArray, self).__init__(rules)
        assert isinstance(self._rules, (list, tuple))

    def __repr__(self):
        ret = []
        for i in range(len(self)):
            if i in self._val:
                ret.append(self._val[i].__repr__())
            elif not (ret and ret[-1] == '...'):
                ret.append('...')
        return "<%s: [%s]>" % (self.__class__.__name__, ','.join(ret))

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        ret = self._val.get(k1)
        if k2:
            ret = ret[k2] if isinstance(ret, (NodeComposite, NodeDocument)) else None
        return ret

    def __setslice__(self, start, stop, other):
        raise NotImplemented

    def __delslice__(self, start, stop):
        start, stop = self.__start_stop(start, stop)
        for i in range(stop - 1, start - 1, -1):
            self.__delitem__(i)

    def __len__(self):
        raise NotImplemented

    def __contains__(self, item):
        item = self._cast(item)
        for i in self._val.values():
            if item == i.value():
                return True
        return False

    def __start_stop(self, start, stop):
        return max(0, start), max(0, min(stop, len(self)))

    def __getslice__(self, start, stop):
        start, stop = self.__start_stop(start, stop)
        return [self._val[i].value() if i in self._val else None
                for i in range(start, stop)]

    def __add__(self, other):
        return self.value() + self._cast(other)

    def __radd__(self, other):
        return self._cast(other) + self.value()

    def keys(self):
        return self._val.keys()

    def set(self, value):
        ret = False
        for k, v in enumerate(self._cast(value)):
            try:
                if self.__setitem__(k, v):
                    ret = True
            except IndexError:
                return ret
        return ret

    def value(self, fields=None, default=None):
        if fields:
            ret = [self.__getitem__(i) for i in fields]
        else:
            ret = self[:]
        if default is not None and not ret:
            ret = default
        return ret


class NodeTuple(NodeArray):

    def __len__(self):
        return len(self._rules)

    def __setitem__(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        if k1 >= len(self._rules):
            raise IndexError(k1)
        ret = False
        if k1 not in self._val:
            self._val[k1] = self.make(self._rules[k1])
            ret = True
        if (k2 and self._val[k1].__setitem__(k2, value)) or self._val[k1].set(value):
            ret = True
        if ret:
            self._inc_changed(k1)
        return ret

    def __delitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        if k1 >= len(self):
            raise IndexError(k1)
        if k2:
            return self._del_sub_item(k1, k2)
        self._val[k1] = self.make(self._rules[k1])
        self._dec_changed(k1)
        return True

    # def __setslice__(self, start, stop, other):
    #     start, stop = self.__start_stop(start, stop)
    #     self.__delslice__(start, stop)
    #     for k, v in enumerate(self._cast(other)):
    #         self.insert(k+start, v)

    def insert(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        if k2:
            self._val[k1].insert(k2, value)
        else:
            self.__setitem__(k1, value)

    def clear(self):
        self._val = {k: self.make(v) for k, v in enumerate(self._rules)}
        self._changed.clear()
        self._removed.clear()

    @property
    def query(self):
        # TODO: не весь _val а только измененные
        if not self._changed:
            if self._removed:
                return {"$set": {i: None for i in self._removed}}
            else:
                return {}

        ret = [self._val[i].value() if i in self._val else None for i in range(len(self))]
        return {"$set": ret}


class NodeList(NodeArray):
    def __init__(self, rules):
        super(NodeList, self).__init__(rules)
        if not self._rules:
            self._rules = [None]
        assert len(self._rules) == 1

    def __len__(self):
        k = self._val.keys()
        return max(k + [0, len(k)])

    def __setitem__(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        ret = False
        if k1 not in self._val:
            self._val[k1] = self.make(self._rules[0])
            ret = True
        if (k2 and self._val[k1].__setitem__(k2, value)) or self._val[k1].set(value):
            ret = True
        if ret:
            self._inc_changed(k1)
        return ret

    def __delitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        if k1 < len(self):
            if k2:
                return self._del_sub_item(k1, k2)
            tmp = {}
            for k, v in self._val.items():
                if k < k1:
                    tmp[k] = v
                elif k > k1:
                    tmp[k - 1] = v
            self._dec_changed(k1)
            self._changed = {i if i < k1 else i - 1 for i in self._changed}
            self._removed = {i if i < k1 else i - 1 for i in self._removed}
            self._val = tmp
            return True

    def __setslice__(self, start, stop, other):
        start, stop = self.__start_stop(start, stop)
        self.__delslice__(start, stop)
        for k, v in enumerate(self._cast(other)):
            self.insert(k + start, v)

    def __iadd__(self, other):
        for i in self._cast(other):
            self.append(i)
        return self

    def _insert_sub_item(self, k1, k2, value):
        if k1 not in self._val:
            self._val[k1] = self.make(self._rules[0])
            self._changed = {i if i < k1 else i + 1 for i in self._changed}
            self._removed = {i if i < k1 else i + 1 for i in self._removed}
        self._val[k1].insert(k2, value)

    def insert(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        if k2:
            self._insert_sub_item(k1, k2, value)
            return
        if k1 < len(self):
            tmp = {}
            for k, v in self._val.items():
                if k >= k1:
                    tmp[k + 1] = v
                else:
                    tmp[k] = v
            self._val = tmp
            self._changed = {i if i < k1 else i + 1 for i in self._changed}
            self._removed = {i if i < k1 else i + 1 for i in self._removed}
        self.__setitem__(k1, value)

    def append(self, value):
        self[len(self)] = value

    @property
    def query(self):
        # TODO: не весь _val а только измененные
        ret = [self._val[i].value() if i in self._val else None for i in range(len(self))]
        return {"$set": ret}


class NodeDict(NodeComposite):
    def __init__(self, rules):
        super(NodeDict, self).__init__(rules)
        assert isinstance(self._rules, dict)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__,
                             {k: v.__repr__() for k, v in self._val.items()})

    def __len__(self):
        return len(self._val)

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        ret = self._val.get(k1)
        if k2:
            ret = ret[k2] if isinstance(ret, (NodeComposite, NodeDocument)) else None
        return ret

    def __setitem__(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if k1 not in self._val:
            if not self._rules:
                if isinstance(value, (list, tuple, NodeArray)):
                    _t = []
                elif isinstance(value, (dict, NodeDict)):
                    _t = {}
                else:
                    _t = None
                self._val[k1] = self.make(_t)
            elif k1 in self._rules:
                self._val[k1] = self.make(self._rules.get(k1))
            else:
                raise KeyError(k1)

        if (k2 and self._val[k1].__setitem__(k2, value)) or self._val[k1].set(value):
            self._inc_changed(k1)
            return True

        return False

    def __delitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if k2:
            return self._del_sub_item(k1, k2)
        if self._rules:
            self._val[k1] = self.make(self._rules.get(k1))
            self._dec_changed(k1)
            return True
        elif k1 in self._val:
            del self._val[k1]
            self._dec_changed(k1)
            return True
        return False

    def __contains__(self, item):
        return item in self._val

    def keys(self):
        return self._rules.keys() if self._rules else self._val.keys()

    def set(self, value):
        ret = False
        if isinstance(value, dict):
            for k, v in self._cast(value).items():
                try:
                    if self.__setitem__(k, v):
                        ret = True
                except KeyError:
                    pass
        return ret

    def clear(self):
        self._val = {k: self.make(v) for k, v in self._rules.items()}
        self._changed.clear()
        self._removed.clear()

    def items(self):
        return self.value().items()

    def values(self):
        return self.value().values()

    def update(self, value):
        if isinstance(value, dict):
            for k, v in value.items():
                self[k] = v
        elif isinstance(value, NodeDict):
            for k, v in value.items():
                self[k] = v.value()
        else:
            raise TypeError

    def value(self, fields=None, default=None):
        ret = {i: self._cast(self.__getitem__(i)) for i in fields or self._val.keys()}
        if default is not None and not ret:
            ret = default
        return ret

    @property
    def query(self):
        ret = {"$set": {}, "$unset": {}}
        if self._rules and self._removed:
            ret["$unset"] = {i: "" for i in self._removed}

        for i in self._changed:
            v = self._val[i]
            if isinstance(v, NodeDocument):
                ref = v.dbref
                ret["$set"][i] = ref if ref.id else None

            else:
                _q = v.query
                for j in ["$set", "$unset"]:
                    if j in _q:
                        _v = _q[j]
                        if isinstance(_v, dict):
                            for k, v in _v.items():
                                ret[j]["%s.%s" % (i, k)] = v
                        else:
                            ret[j][i] = _v
        if not ret["$set"]:
            del ret["$set"]
        if not ret["$unset"]:
            del ret["$unset"]
        return ret

# TODO: add default rule fields = {'f_0': 'Foo', 'f_1': datetime.datetime.now}
