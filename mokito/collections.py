import copy

from .fields import Field
from .tools import make_field, SEPARATOR
from .errors import MokitoDBREFError


class CollectionField(Field):
    def __init__(self, _parent=None, **kwargs):
        super().__init__(_parent=_parent, **kwargs)
        self._val = {}
        self._dirty_fields = {}

    @property
    def dirty_fields(self):
        return list(self._dirty_fields.keys())

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def _test_item(self, key):
        raise NotImplementedError

    def _sep_key(self, key):
        k1, _, k2 = str(key).partition(SEPARATOR)
        return k1, k2


class ArrayField(CollectionField):
    def __len__(self):
        return max(map(int, self._val.keys())) + 1 if self._val else 0

    def __iter__(self):
        for i in range(len(self)):
            yield self.__getitem__(i)

    def _sep_key(self, key):
        k1, k2 = super()._sep_key(key)
        try:
            ik1 = int(k1)
        except ValueError:
            raise TypeError("%s indices must be integers" % self.__class__.__name__)
        if ik1 < 0:
            ik1 += len(self)
            k1 = str(ik1)
        return k1, k2

    @property
    def dirty_fields(self):
        return list(map(int, self._dirty_fields.keys()))

    def dirty_clear(self):
        from .documents import Document
        self.dirty = False
        for i in self._val.values():
            if not isinstance(i, Document):
                i.dirty_clear()
        self._dirty_fields = {}

    def get_dirty(self):
        from .documents import Document
        if not self._dirty:
            for i in self._val.values():
                if not isinstance(i, Document) and i.dirty:
                    self.dirty = True
                    break
        return self._dirty

    dirty = property(get_dirty, CollectionField.set_dirty)

    def set_value(self, value, **kwargs):
        from .documents import Document, Model

        if isinstance(value, (list, tuple)):
            value = {str(k): v for k, v in enumerate(value)}

        elif value is None:
            self.clear()
            return

        if not isinstance(value, dict):
            raise TypeError()

        value = self.validate(value, **kwargs)

        for key, v in value.items():
            k1, k2 = self._sep_key(key)
            item = self._test_item(k1)

            if k2:
                item.set_value({k2: v}, **kwargs)
            else:
                if isinstance(item, Document):
                    if v is None:
                        del self[k1]
                    elif isinstance(v, Document):
                        self._val[k1] = v
                        if item.id != v.id:
                            self._dirty = True
                    else:
                        item.set_value(v, **kwargs)

                elif isinstance(v, Model):
                    item.set_value(v.value, **kwargs)

                else:
                    item.set_value(v, **kwargs)

    def get_value(self, **kwargs):
        return [self._val[i].get_value(**kwargs) if i in self._val else None for i in map(str, range(len(self)))]

    value = property(get_value, set_value)

    def update_values(self, *args, **kwargs):
        for k, v in enumerate(args):
            self[k].value = v

        for k, v in kwargs.items():
            self[k].value = v

    @property
    def self_value(self):
        return [self._val[i].self_value if i in self._val else None for i in map(str, range(len(self)))]

    def make_query(self, short=False):
        from .documents import Document

        if not self.dirty:
            return {}

        ret = {"$set": []}
        for k in range(len(self)):
            k = str(k)
            v = self._val.get(k)

            if v is None:
                ret["$set"].append(None)

            elif isinstance(v, Document):
                if v.dirty or v.make_query(True):
                    if v.id is None:
                        raise MokitoDBREFError(v)
                ret["$set"].append(v.dbref)

            else:
                ret["$set"].append(v.get_value(inner=True))

            if short and ret['$set']:
                return True
        return ret

    query = property(make_query)


class ListField(ArrayField):
    def __init__(self, rules, _parent=None, **kwargs):
        super().__init__(_parent=_parent, **kwargs)
        if not rules:
            rules = [None]
        self._default = False
        _rules = [make_field(i, _parent=self) for i in rules]
        self._rules = copy.deepcopy(_rules[0])
        for k, v in enumerate(_rules):
            if v._default:
                self._default = True
                v._parent = self
                self._val[str(k)] = v

    def _test_item(self, key):
        key = str(key)
        if key not in self._val:
            self.dirty = True
            item = copy.deepcopy(self._rules)
            item._parent = self
            self._val[key] = item
        return self._val[key]

    def __getitem__(self, key):
        k1, k2 = self._sep_key(key)
        item = self._test_item(k1)
        try:
            return item[k2] if k2 else item
        except TypeError:
            raise IndexError('Out of range')

    def __setitem__(self, key, value):
        from .fields import AnyField

        k1, k2 = self._sep_key(key)
        item = self._test_item(k1)
        if k2:
            item[k2] = value
        else:
            if value is None:
                del self[k1]
            elif isinstance(self._rules, AnyField) or value.__class__ == self._rules.__class__:
                self._val[k1] = value
            else:
                raise TypeError('%s is not %s' % (value.__class__.__name__, self._rules.__class__.__name__))

    def __delitem__(self, key):
        k1, k2 = self._sep_key(key)
        if not k2 and k1 in self._val:
            self.dirty = True
        item = self._test_item(k1)
        if k2:
            del item[k2]

        else:
            del self._val[k1]
            keys = [int(i) for i in self._val.keys()]
            keys.sort()
            ik1 = int(k1)
            for i in keys:
                if i > ik1:
                    item = self._val.pop(str(i))
                    if item.value is not None:
                        self._val[str(i - 1)] = item

    def clear(self):
        self._val = {}
        self.dirty = True

    def append(self, value):
        self[len(self)] = value

    def append_value(self, value, **kwargs):
        item = self._test_item(str(len(self)))
        value = self.validate(value, **kwargs)
        item.set_value(value, **kwargs)

    def pop(self, key=-1):
        k1, k2 = self._sep_key(key)
        item = self._test_item(k1)
        if k2:
            return item.pop(k2)
        del self[k1]
        return item


class TupleField(ArrayField):
    def __init__(self, rules, _parent=None, **kwargs):
        super().__init__(_parent=_parent, **kwargs)
        self._default = False
        for k, v in enumerate(rules):
            item = make_field(v, _parent=self)
            if item._default:
                self._default = True
            self._val[str(k)] = item

    def _test_item(self, key):
        try:
            return self._val[key]
        except KeyError:
            raise IndexError("%s out of range" % key)

    def __getitem__(self, key):
        k1, k2 = self._sep_key(key)
        item = self._test_item(k1)
        try:
            return item[k2] if k2 else item
        except TypeError:
            raise IndexError('Out of range')

    def __setitem__(self, key, value):
        from .fields import AnyField

        k1, k2 = self._sep_key(key)
        item = self._test_item(k1)
        if k2:
            item[k2] = value
        else:
            if value is None:
                del self[k1]
            elif isinstance(item, AnyField) or value.__class__ == item.__class__:
                self._val[k1] = value
            else:
                raise TypeError('%s not %s' % (value.__class__.__name__, item.__class__.__name__))

    def __delitem__(self, key):
        k1, k2 = self._sep_key(key)
        item = self._test_item(k1)
        if k2:
            del item[k2]
        else:
            item.set_value(None)
        self.dirty = True

    def clear(self):
        for k, v in self._val.items():
            if isinstance(v, (ArrayField, DictField)):
                v.clear()
            else:
                self[k] = None

        self.dirty = True


class DictField(CollectionField):
    def __init__(self, rules, _parent=None, **kwargs):
        super().__init__(_parent=_parent, **kwargs)
        # TODO: убрать безрулевые, т.е. {}
        self._default = False
        self._rules = bool(rules)
        if rules:
            for k, v in rules.items():
                item = make_field(v, _parent=self)
                if item._default:
                    self._default = True
                self._val[k] = item

    def __len__(self):
        return len(self._val)

    def _test_item(self, key):
        from .fields import AnyField

        if not self._rules and key not in self._val:
            self._val[key] = AnyField(_parent=self)
        return self._val[key]

    def __getitem__(self, key):
        k1, k2 = self._sep_key(key)
        item = self._test_item(k1)
        return item[k2] if k2 else item

    def __setitem__(self, key, value):
        from .fields import AnyField

        k1, k2 = self._sep_key(key)
        item = self._test_item(k1)
        if k2:
            item[k2] = value

        else:
            if value is None:
                self._dirty_fields[k1] = True
                self[k1].set_value(None)

            elif not self._rules or isinstance(item, AnyField) or value.__class__ == item.__class__:
                self._dirty_fields[k1] = True
                self._val[k1] = value

            else:
                raise TypeError('%s not %s' % (value.__class__.__name__, item.__class__.__name__))

    def __delitem__(self, key):
        k1, k2 = self._sep_key(key)
        if k2:
            del self._val[k1][k2]
        else:
            if not self._rules:
                del self._val[k1]
            else:
                self._val[k1].clear()
            self._dirty_fields[k1] = False

    def get_value(self, **kwargs):
        return {k: v.get_value(**kwargs) for k, v in self._val.items()}

    def set_value(self, value, **kwargs):
        from .documents import Document, Model

        if value is None:
            self.clear()
            return

        if not isinstance(value, dict):
            raise TypeError()

        value = self.validate(value, **kwargs)

        for key, v in value.items():
            k1, k2 = self._sep_key(key)
            item = self._test_item(k1)

            if k2:
                item.set_value({k2: v}, **kwargs)
            else:
                if isinstance(item, Document):
                    if v is None:
                        del self[k1]
                    elif isinstance(v, Document):
                        self._val[k1] = v
                        if item.id != v.id:
                            self._dirty_fields[k1] = True
                    else:
                        item.set_value(v, **kwargs)

                elif isinstance(v, Model):
                    item.set_value(v.value, **kwargs)

                else:
                    item.set_value(v, **kwargs)

    value = property(get_value, set_value)

    def update_values(self, **kwargs):
        for k, v in kwargs.items():
            self[k].value = v

    @property
    def self_value(self):
        return {k: v.self_value for k, v in self._val.items()}

    def dirty_clear(self):
        from .documents import Document
        for i in self._val.values():
            if not isinstance(i, Document):
                i.dirty_clear()
        self._dirty_fields = {}

    def items(self):
        return self._val.items()

    @property
    def dirty(self):
        from .documents import Document
        if self._dirty_fields:
            return True
        for k, v in self._val.items():
            if not isinstance(v, Document) and v.dirty:
                self._dirty_fields[k] = True
                # print('X5', self._dirty_fields)
                return True
        return False

    def clear(self):
        self._dirty_fields = {i: False for i in self._val.keys()}
        if self._rules:
            for i in self._val.values():
                i.clear()
        else:
            self._val = {}

    def make_query(self, short=False):
        from .documents import Document
        # from .models import Model
        ret = {"$set": {}, "$unset": {}}

        if not self._rules:
            ret['$set'] = self.get_value(inner=True)

        else:
            for k, v in self._val.items():
                if isinstance(v, Document):
                    _d = self._dirty_fields.get(k, None)
                    if _d is False:
                        ret["$unset"][k] = ''
                    elif (_d is True) or v.ref_changed:
                        if v.id is None:
                            raise MokitoDBREFError(v)
                        ret["$set"][k] = v.dbref

                elif k in self._dirty_fields or v.dirty:
                    # print('X7', self._dirty_fields)
                    if isinstance(v, ArrayField):
                        _q = v.query
                        if _q:
                            ret["$set"][k] = _q["$set"]

                    # elif isinstance(v, Model):
                    #     _q = v.query
                    #     for j in ["$set", "$unset"]:
                    #         if j in _q:
                    #             for k1, v1 in _q[j].items():
                    #                 ret[j]["%s.%s" % (k, k1)] = v1

                    elif isinstance(v, DictField):
                        _q = v.query
                        for j in ["$set", "$unset"]:
                            if j in _q:
                                if v._rules:
                                    for k1, v1 in _q[j].items():
                                        ret[j]["%s.%s" % (k, k1)] = v1
                                else:
                                    ret[j][k] = _q[j]
                    else:
                        ret['$set'][k] = v.value

                    if short and (ret['$set'] or ret['$unset']):
                        return True

        if not ret["$set"]:
            del ret["$set"]
        if not ret["$unset"]:
            del ret["$unset"]
        return ret

    query = property(make_query)
