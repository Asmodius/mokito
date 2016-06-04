# coding: utf-8

# TODO: add docstring

import copy

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

    def value(self):
        return self._val

    def __str__(self):
        return str(self.value())

    def changed_clear(self):
        self._changed = False

    def _get_changed(self):
        return self._changed

    @property
    def changed(self):
        return self._get_changed()


class NodeComposite(Node):
    def __init__(self, rules):
        super(NodeComposite, self).__init__(rules)
        self._changed = set()
        self._val = {}
        self.clear()

    def __contains__(self, item):
        raise NotImplemented

    def _get_changed(self):
        for k, v in self._val.items():
            if v.changed:
                self._changed.add(k)
        return list(self._changed)

    def changed_clear(self):
        self._changed.clear()
        map(lambda i: i.changed_clear(), self._val.values())


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
                for i in range(start, stop+1)]

    def __add__(self, other):
        return self.value() + self._cast(other)

    def __radd__(self, other):
        return self._cast(other) + self.value()

    def set(self, value):
        ret = False
        for k, v in enumerate(self._cast(value)):
            if self.__setitem__(k, v):
                ret = True
        return ret

    def clear(self):
        self._val = {}
        self._changed = set()

    def value(self):
        return self[:]


class NodeTuple(NodeArray):

    def __len__(self):
        return len(self._rules)

    def __setitem__(self, key, value):
        k1, _, k2 = str(key).partition(SEPARATOR)
        k1 = int(k1)
        ret = False
        if k1 < len(self._rules):
            if k1 not in self._val:
                self._val[k1] = self._maker(self._rules[k1])
                ret = True
            if (k2 and self._val[k1].__setitem__(k2, value)) or self._val[k1].set(value):
                ret = True
            if ret:
                self._changed.add(k1)
        return ret

    def clear(self):
        self._val = {k: self._maker(v) for k, v in enumerate(self._rules)}
        self._changed = set()


class NodeList(NodeArray):
    def __init__(self, rules):
        super(NodeList, self).__init__(rules)
        if not self._rules:
            self._rules = [None]
        assert len(self._rules) == 1

    def __len__(self):
        return max(self._val.keys()+[0])

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
            self._changed.add(k1)
        return ret

    def __delitem__(self, key):
        if key < len(self):
            tmp = {}
            for k, v in self._val.items():
                if k < key:
                    tmp[k] = v
                elif k > key:
                    tmp[k-1] = v
            self._changed.discard(key)
            self._changed = {i if i < key else i - i for i in self._changed}
            self._val = tmp

    def __setslice__(self, start, stop, other):
        start, stop = self.__start_stop(start, stop)
        self.__delslice__(start, stop)
        for k, v in enumerate(self._cast(other)):
            self.insert(k+start, v)

    def __delslice__(self, start, stop):
        start, stop = self.__start_stop(start, stop)
        for i in range(stop, start, -1):
            self.__delitem__(i)

    def __iadd__(self, other):
        for i in other:
            self.append(i)
        return self

    def insert(self, key, value):
        if key < len(self):
            tmp = {}
            for k, v in self._val.items():
                if k >= key:
                    tmp[k+1] = v
                else:
                    tmp[k] = v
            self._val = tmp
            self._changed = {i if i < key else i+1 for i in self._changed}
        self.__setitem__(key, value)

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
        k1, _, k2 = key.partition(SEPARATOR)
        if not self._rules:
            self._val[k1] = self._maker(type(value))
        elif k1 in self._rules and k1 not in self._val:
            self._val[k1] = self._maker(self._rules.get(k1))

        if k1 in self._val:
            if (k2 and self._val[k1].__setitem__(k2, value)) or self._val[k1].set(value):
                self._changed.add(k1)
                return True

    def __delitem__(self, key):
        if self._rules:
            self._val[key] = self._maker(self._rules.get(key))
            self._changed.add(key)
        elif key in self._val:
            del self._val[key]
            self._changed.discard(key)

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
        self._changed = set()

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


if __name__ == "__main__":

    rul = {
        # '_id': ObjectId,
        # 'f_0': None,
        # 'f_1': str,
        # 'f_2': int,
        # 'f_3': bool,
        # 'f_4': float,
        # 'f_5': datetime.datetime,
        # 'f_6': {'f_6_1': int, 'f_6_2': str, 'f_6_3': {}, 'f_6_4': {}},
        # 'f_7': [None],
        # 'f_8': [str],
        'f_9': [{'f_9_1': int, 'f_9_2': str, 'f_9_3': {}}],
        # 'f_10': (int, str),
    }

    dat = {
        # '_id': ObjectId('574fb41b48704c32d9a51e67'),
        # 'f_0': 'foo',
        # 'f_1': 100,
        # 'f_2': 100,
        # 'f_3': True,
        # 'f_4': .5,
        # 'f_5': datetime.datetime(2016, 6, 2, 7, 20, 43),
        # 'f_6': {'f_6_1': 200, 'f_6_2': 'string'},
        # 'f_7': [1, 'foo', .2],
        'f_8': ['a', 1, 'c'],
        'f_9': [
            {'f_9_1': 100, 'f_9_2': 's1', 'f_9_3': {'a': 1}},
            {'f_9_1': 200, 'f_9_2': 's2', 'f_9_3': {'b': 2}},
        ],
        # 'f_10': [200, 'string', 1],
     }

    # class Document(object):
    #     _ruler = NodeDict(rul)
    #
    #     def __init__(self):
    #         self.data = copy.copy(self._ruler)
    #         self.data.set(dat)
    #
    # m = Document()
    # print
    # print m.data
    # # print m.data['f_8'].changed
    # # del m.data['f_8'][1]
    #
    # # m.data['f_8'][1] = 100
    # # m.data['f_8.1'] = 100
    # m.data['f_9.0.f_9_1'] = 500
    #
    # # print m.data.changed
    # # print m.data['f_8'].changed
    #
    # print m.data.value()

    # class Document(object):
    #     #_ruler = NodeDict({})
    #     _ruler = NodeDict(dict)
    #
    #     def __init__(self):
    #         self.data = copy.copy(self._ruler)
    #         self.data.set({'foo': 'bar'})
    #
    # m = Document()
    # print
    # print m.data
    # print m.data.value()
    # print m.data.changed
    # # print m.data['f_8'].changed
    # # del m.data['f_8'][1]
    #
    # # m.data['f_8'][1] = 100
    # # m.data['f_8.1'] = 100
    # #m.data['f_9.0.f_9_1'] = 500
    #
    # # print m.data.changed
    # # print m.data['f_8'].changed

    x1 = {
        # 'f_1': 'bar',
        # 'f_2': {
        #     'a': 1,
        #     'b': .2
        # },
        'f_3': [1, 'a', 3]
    }

    node1 = NodeDict(dict)
    node1.set(x1)
    #node1['f_1'] = 100
    print node1.value()
    z = node1['f_3.2']
    print z
    node1['f_3.2'] = 100
    print node1.value()