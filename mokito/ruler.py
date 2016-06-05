# coding: utf-8

# TODO: add docstring

__all__ = ["Node", "NodeTuple", "NodeList", "NodeDict"]

SEPARATOR = '.'


class Node(object):
    def __init__(self, rules):
        self._changed = False
        self._val = None
        self._rules = self._normalize(rules)

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

    def _maker(self, data_type):
        data_type = self._normalize(data_type)

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


class NodeComposite(Node):
    def __init__(self, rules):
        super(NodeComposite, self).__init__(rules)
        self._changed = set()
        self._removed = set()
        self._val = {}
        self.clear()

    def __contains__(self, item):
        raise NotImplemented

    def __getitem__(self, key):
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

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        ret = self._val.get(k1)
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
        for i in range(stop-1, start-1, -1):
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

    def value(self):
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
            self._val[k1] = self._maker(self._rules[k1])
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
        self._val[k1] = self._maker(self._rules[k1])
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
        self._val = {k: self._maker(v) for k, v in enumerate(self._rules)}
        self._changed.clear()
        self._removed.clear()


class NodeList(NodeArray):
    def __init__(self, rules):
        super(NodeList, self).__init__(rules)
        if not self._rules:
            self._rules = [None]
        assert len(self._rules) == 1

    def __len__(self):
        k = self._val.keys()
        return max(k+[0, len(k)])

    def __setitem__(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        ret = False
        if k1 not in self._val:
            self._val[k1] = self._maker(self._rules[0])
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
                    tmp[k-1] = v
            self._dec_changed(k1)
            self._changed = {i if i < k1 else i - 1 for i in self._changed}
            self._removed = {i if i < k1 else i - 1 for i in self._removed}
            self._val = tmp
            return True

    def __setslice__(self, start, stop, other):
        start, stop = self.__start_stop(start, stop)
        self.__delslice__(start, stop)
        for k, v in enumerate(self._cast(other)):
            self.insert(k+start, v)

    def __iadd__(self, other):
        for i in self._cast(other):
            self.append(i)
        return self

    def _insert_sub_item(self, k1, k2, value):
        if k1 not in self._val:
            self._val[k1] = self._maker(self._rules[0])
            self._changed = {i if i < k1 else i+1 for i in self._changed}
            self._removed = {i if i < k1 else i+1 for i in self._removed}
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
                    tmp[k+1] = v
                else:
                    tmp[k] = v
            self._val = tmp
            self._changed = {i if i < k1 else i+1 for i in self._changed}
            self._removed = {i if i < k1 else i+1 for i in self._removed}
        self.__setitem__(k1, value)

    def append(self, value):
        self[len(self)] = value


class NodeDict(NodeComposite):
    def __init__(self, rules):
        super(NodeDict, self).__init__(rules)
        assert isinstance(self._rules, dict)

    def __len__(self):
        return len(self._val)

    def __getitem__(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        ret = self._val.get(k1)
        if k2:
            ret = ret[k2] if isinstance(ret, NodeComposite) else None
        return ret

    def __setitem__(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        if k1 not in self._val:
            if not self._rules:
                _t = self._maker([] if isinstance(value, (list, type, NodeArray)) else None)
                self._val[k1] = _t
            elif k1 in self._rules:
                self._val[k1] = self._maker(self._rules.get(k1))
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
            self._val[k1] = self._maker(self._rules.get(k1))
            self._inc_changed(k1)
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
        for k, v in self._cast(value).items():
            if self.__setitem__(k, v):
                ret = True
        return ret

    def clear(self):
        self._val = {k: self._maker(v) for k, v in self._rules.items()}
        self._changed.clear()
        self._removed.clear()

    def keys(self):
        return self._val.keys()

    def items(self):
        return self.value().items()

    def values(self):
        return self.value().values()

    def update(self, data):
        if isinstance(data, dict):
            for k, v in data.items():
                self[k] = v
        elif isinstance(data, NodeDict):
            for k, v in data.items():
                self[k] = v.value()
        else:
            raise TypeError

    def get(self, key, default=None):
        if key not in self._val:
            return default
        return self[key]

    def setdefault(self, key, default=None):
        if key not in self._val:
            self[key] = default
        return self[key]

    def pop(self, key, default=None):
        ret = self.get(key, default)
        self.__delitem__(key)
        return ret

    def value(self):
        return {k: v.value() for k, v in self._val.items()}
