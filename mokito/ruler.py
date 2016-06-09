# coding: utf-8

__all__ = ["Node", "NodeTuple", "NodeList", "NodeDict"]

SEPARATOR = '.'

# TODO: Node.value(fields=None)


class Node(object):
    def __init__(self, rules):
        self._changed = False
        self._val = None
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

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.value())

    def __str__(self):
        return str(self.value())

    @staticmethod
    def _cast(other):
        return other.value() if isinstance(other, Node) else other

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

    def changed_clear(self):
        self._changed = False

    def value(self):
        return self._val

    @property
    def dirty(self):
        return self._changed

    def query(self):
        return {"$set": self._val}


class NodeComposite(Node):
    def __init__(self, rules):
        super(NodeComposite, self).__init__(rules)
        self._changed = set()
        self._removed = set()
        self._val = {}
        self.clear()

    def __contains__(self, item):
        raise NotImplemented

    def __getitem__(self, key, default=None):
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

    def get(self, key, default=None):
        return self.__getitem__(key, default)

    def clear(self):
        self._val = {}
        self._changed.clear()
        self._removed.clear()

    def changed_clear(self):
        self._changed.clear()
        self._removed.clear()
        map(lambda i: i.changed_clear(), self._val.values())

    def insert(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if k2:
            self._val[k1].insert(k2, value)
        raise AttributeError('object has no attribute "insert"')

    @property
    def dirty(self):
        for k, v in self._val.items():
            if v.dirty:
                self._inc_changed(k)
        return bool(self._changed or self._removed)


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

    def __getitem__(self, key, default=None):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        ret = self._val.get(k1, default)
        if k2:
            ret = ret[k2] if isinstance(ret, NodeComposite) else None
        return ret

    def __setitem__(self, key, value):
        raise NotImplemented

    def __delitem__(self, key):
        raise NotImplemented

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

    def set(self, value):
        ret = False
        for k, v in enumerate(self._cast(value)):
            try:
                if self.__setitem__(k, v):
                    ret = True
            except IndexError:
                return ret
        return ret

    def value(self, fields=None):
        if fields:
            return [self.__getitem__(i) for i in fields]
        return self[:]


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

    def query(self):
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

    def query(self):
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

    def __getitem__(self, key, default=None):
        k1, _, k2 = str(key).partition(SEPARATOR)
        ret = self._val.get(k1, default)
        if k2:
            ret = ret[k2] if isinstance(ret, NodeComposite) else None
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

    def keys(self):
        return self._val.keys()

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

    def setdefault(self, key, default=None):
        if self._val.get(key).value() is None:
            self.__setitem__(key, default)
        return self.__getitem__(key)

    def pop(self, key, default=None):
        ret = self.get(key, default)
        self.__delitem__(key)
        return ret

    def value(self, fields=None):
        return {i: self._cast(self.get(i)) for i in fields or self._val.keys()}

    def query(self):
        ret = {"$set": {}, "$unset": {}}
        if self._rules and self._removed:
            ret["$unset"] = {i: "" for i in self._removed}

        for i in self._changed:
            _q = self._val[i].query()
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
