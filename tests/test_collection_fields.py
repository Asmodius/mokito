# coding: utf-8

import unittest
import datetime

from bson import ObjectId

from mokito.fields import (
    Field,
    IntField,
    FloatField,
    StringField,
    BooleanField,
    ObjectIdField,
    DateTimeField,
    DictField,
    TupleField,
    ListField,
    ChoiceField
)


class TestCollectionFields(unittest.TestCase):
    def test_list_field_1(self):
        f = Field.make([None])
        self.assertIsInstance(f, ListField)
        self.assertIsInstance(f._rules, Field)

        f = Field.make([int])
        self.assertIsInstance(f, ListField)
        self.assertIsInstance(f._rules, IntField)

        f = Field.make([IntField])
        self.assertIsInstance(f._rules, IntField)

        f = Field.make([float])
        self.assertIsInstance(f, ListField)
        self.assertIsInstance(f._rules, FloatField)

        f = Field.make([str])
        self.assertIsInstance(f, ListField)
        self.assertIsInstance(f._rules, StringField)

        f = Field.make([bool])
        self.assertIsInstance(f, ListField)
        self.assertIsInstance(f._rules, BooleanField)

        f = Field.make([datetime.datetime])
        self.assertIsInstance(f, ListField)
        self.assertIsInstance(f._rules, DateTimeField)

        f = Field.make([ObjectId])
        self.assertIsInstance(f, ListField)
        self.assertIsInstance(f._rules, ObjectIdField)

    def test_list_field_2(self):
        data = [str]
        f = Field.make(data)

        for i in [0, '0', '0.0', 'a']:
            with self.assertRaises(IndexError):
                _ = f[i]

    def test_list_field_3(self):
        f = Field.make([str])
        self.assertEqual(f.value, [])
        self.assertEqual(f.self_value, [])
        self.assertEqual(f.get(), [])

        f[1] = 'foo'
        self.assertEqual(f.value, [None, 'foo'])
        self.assertEqual(f.self_value, [None, 'foo'])
        self.assertEqual(f.get(), [None, 'foo'])

        f.append('bar')
        self.assertEqual(f.value, [None, 'foo', 'bar'])
        self.assertEqual(f.self_value, [None, 'foo', 'bar'])
        self.assertEqual(f.get(), [None, 'foo', 'bar'])

        f['3'] = 'x'
        self.assertEqual(f.value, [None, 'foo', 'bar', 'x'])
        self.assertEqual(f.self_value, [None, 'foo', 'bar', 'x'])
        self.assertEqual(f.get(), [None, 'foo', 'bar', 'x'])
        self.assertEqual(f.get(2, 1), ['bar', 'foo'])

        self.assertIsNone(f.pop(0).get())
        self.assertEqual(f.value, ['foo', 'bar', 'x'])
        self.assertEqual(f.self_value, ['foo', 'bar', 'x'])
        self.assertEqual(f.get(), ['foo', 'bar', 'x'])

        self.assertEqual(f.pop(1).value, 'bar')
        self.assertEqual(f.value, ['foo', 'x'])
        self.assertEqual(f.self_value, ['foo', 'x'])
        self.assertEqual(f.get(), ['foo', 'x'])

        self.assertEqual(f.pop().get(), 'x')
        self.assertEqual(f.value, ['foo'])
        self.assertEqual(f.self_value, ['foo'])
        self.assertEqual(f.get(), ['foo'])

        self.assertEqual(f.pop(3, default=123).get(), '123')
        self.assertEqual(f.value, ['foo'])
        self.assertEqual(f.self_value, ['foo'])
        self.assertEqual(f.get(), ['foo'])

        f[2] = 'zzz'
        self.assertEqual(f.value, ['foo', None, 'zzz'])
        self.assertEqual(f.self_value, ['foo', None, 'zzz'])
        self.assertEqual(f.get(), ['foo', None, 'zzz'])

        del f[0]
        self.assertEqual(f.value, [None, 'zzz'])
        self.assertEqual(f.self_value, [None, 'zzz'])
        self.assertEqual(f.get(), [None, 'zzz'])

        f.set(['foo', 'bar'])
        self.assertEqual(f.value, ['foo', 'bar'])
        self.assertEqual(f.self_value, ['foo', 'bar'])
        self.assertEqual(f.get(), ['foo', 'bar'])

        f[1].set(None)
        self.assertEqual(f.value, ['foo', None])
        self.assertEqual(f.self_value, ['foo', None])
        self.assertEqual(f.get(), ['foo', None])
        self.assertEqual(f.get(0, 1), ['foo', None])
        self.assertEqual(f.get(1, 0), [None, 'foo'])

    def test_list_field_4(self):
        dt1 = datetime.datetime.utcnow()
        dt2 = datetime.datetime(2016, 1, 2, 3, 4, 5)

        f = Field.make([datetime.datetime])
        self.assertEqual(f.value, [])
        self.assertEqual(f.self_value, [])
        self.assertEqual(f.get(), [])

        f.set([dt1, dt2])
        self.assertEqual(f.value, [dt1, dt2])
        self.assertEqual(f.self_value, [dt1, dt2])
        self.assertEqual(f.get(), [dt1, dt2])
        self.assertEqual(f.get(date_format='iso'),
                         [dt1.replace(microsecond=0).isoformat(),
                          dt2.replace(microsecond=0).isoformat()])
        self.assertEqual(f.get(date_format='%d/%m/%y'),
                         [dt1.strftime('%d/%m/%y'), dt2.strftime('%d/%m/%y')])
        self.assertEqual(f.get(1, date_format='%d/%m/%y'), [dt2.strftime('%d/%m/%y')])

    def test_tuple_field_1(self):
        data = (None, int, IntField)
        f = Field.make(data)
        self.assertIsInstance(f, TupleField)
        self.assertIsInstance(f._val['0'], Field)
        self.assertIsInstance(f._val['1'], IntField)
        self.assertIsInstance(f._val['2'], IntField)

        data = (float, str, bool, ObjectId, datetime.datetime)
        f = Field.make(data)
        self.assertIsInstance(f, TupleField)
        self.assertIsInstance(f._val['0'], FloatField)
        self.assertIsInstance(f._val['1'], StringField)
        self.assertIsInstance(f._val['2'], BooleanField)
        self.assertIsInstance(f._val['3'], ObjectIdField)
        self.assertIsInstance(f._val['4'], DateTimeField)

    def test_tuple_field_2(self):
        data = (str, int)
        f = Field.make(data)

        for i in [0, '0']:
            self.assertIsNone(f[i].value)
            self.assertIsNone(f[i].self_value)

        with self.assertRaises(TypeError):
            _ = f['0.0']

        with self.assertRaises(IndexError):
            _ = f['a']

        with self.assertRaises(IndexError):
            _ = f[2]

    def test_field_set_2(self):
        f = Field.make((datetime.datetime, str))

        self.assertEqual(f.value, [None, None])
        self.assertEqual(f.self_value, [None, None])
        self.assertEqual(f.get(), [None, None])
        self.assertEqual(f.get(date_format='iso'), [None, None])

        f[1] = 123
        self.assertEqual(f.value, [None, '123'])
        self.assertEqual(f.self_value, [None, '123'])
        self.assertEqual(f.get(), [None, '123'])

        dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
        f[0] = dt1
        self.assertEqual(f.value, [dt1, '123'])
        self.assertEqual(f.self_value, [dt1, '123'])
        self.assertEqual(f.get(), [dt1, '123'])
        self.assertEqual(f.get(date_format='iso'), ['2016-01-02T03:04:05', '123'])

        with self.assertRaises(IndexError):
            f[2] = 'x'

        f[1] = None
        self.assertEqual(f.value, [dt1, None])
        self.assertEqual(f.self_value, [dt1, None])
        self.assertEqual(f.get(), [dt1, None])

        del f[0]
        self.assertEqual(f.value, [None, None])
        self.assertEqual(f.self_value, [None, None])
        self.assertEqual(f.get(), [None, None])

        f.set([dt1, 456])
        self.assertEqual(f.value, [dt1, '456'])
        self.assertEqual(f.self_value, [dt1, '456'])
        self.assertEqual(f.get(), [dt1, '456'])
        self.assertEqual(f.get(date_format='%d/%m/%y'), [dt1.strftime('%d/%m/%y'), '456'])

    def test_dict_field_1(self):
        data = {
            'f0': None,
            'f1': IntField,
            'f2': int,
            'f3': IntField(),
            'f4': float,
            'f5': str,
            'f6': bool,
            'f7': datetime.datetime,
            'f8': ObjectId
        }
        f = Field.make(data)
        self.assertIsInstance(f, DictField)
        self.assertIsInstance(f._val['f0'], Field)
        self.assertIsInstance(f._val['f0'], Field)
        self.assertIsInstance(f._val['f1'], IntField)
        self.assertIsInstance(f._val['f2'], IntField)
        self.assertIsInstance(f._val['f3'], IntField)
        self.assertIsInstance(f._val['f4'], FloatField)
        self.assertIsInstance(f._val['f5'], StringField)
        self.assertIsInstance(f._val['f6'], BooleanField)
        self.assertIsInstance(f._val['f7'], DateTimeField)
        self.assertIsInstance(f._val['f8'], ObjectIdField)

    def test_dict_field_2(self):
        dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
        dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
        id1 = ObjectId()
        data = {
            'd': {
                'd1': datetime.datetime,
                'd2': [str],
                'd3': (ObjectId, str)
            },
            'l': [{'l1': int, 'l2': str}],
            't': (int, {'t1': datetime.datetime, 't2': str}),
        }
        f = Field.make(data)
        self.assertIsInstance(f, DictField)
        self.assertDictEqual(f.value, {
            'd': {'d1': None, 'd2': [], 'd3': [None, None]},
            'l': [],
            't': [None, {'t1': None, 't2': None}],
        })
        self.assertDictEqual(f.self_value, {
            'd': {'d1': None, 'd2': [], 'd3': [None, None]},
            'l': [],
            't': [None, {'t1': None, 't2': None}],
        })
        self.assertDictEqual(f.get(), {
            'd': {'d1': None, 'd2': [], 'd3': [None, None]},
            'l': [],
            't': [None, {'t1': None, 't2': None}],
        })
        self.assertDictEqual(f.get('d'), {
            'd': {'d1': None, 'd2': [], 'd3': [None, None]},
        })

        self.assertIsInstance(f._val['d'], DictField)
        self.assertIsInstance(f['d'], DictField)
        self.assertDictEqual(f['d'].value, {'d1': None, 'd2': [], 'd3': [None, None]})
        self.assertDictEqual(f['d'].self_value, {'d1': None, 'd2': [], 'd3': [None, None]})
        self.assertDictEqual(f['d'].get(), {'d1': None, 'd2': [], 'd3': [None, None]})

        self.assertIsInstance(f._val['l'], ListField)
        self.assertIsInstance(f['l'], ListField)
        self.assertEqual(f['l'].value, [])
        self.assertEqual(f['l'].self_value, [])
        self.assertEqual(f['l'].get(), [])

        self.assertIsInstance(f._val['t'], TupleField)
        self.assertIsInstance(f['t'], TupleField)
        self.assertEqual(f['t'].value, [None, {'t1': None, 't2': None}])
        self.assertEqual(f['t'].self_value, [None, {'t1': None, 't2': None}])
        self.assertEqual(f['t'].get(), [None, {'t1': None, 't2': None}])

        self.assertEqual(f.get('l', 't'), {'l': [], 't': [None, {'t1': None, 't2': None}]})
        self.assertEqual(f.get('d.d3', 'd.d1', 't.1.t1'),
                         {'d': {'d1': None, 'd3': [None, None]}, 't': [{'t1': None}]})
        self.assertEqual(f['d'].get('d1', 'd2'), {'d1': None, 'd2': []})

        f.set({
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': (id1, 'bar')
            },
            'l': [{'l1': 456, 'l2': 'baz'}],
            't': (789, {'t1': dt2, 't2': 'x'}),
        })
        self.assertDictEqual(f.value, {
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [id1, 'bar']
            },
            'l': [{'l1': 456, 'l2': 'baz'}],
            't': [789, {'t1': dt2, 't2': 'x'}]
        })
        self.assertDictEqual(f.self_value, {
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [id1, 'bar']
            },
            'l': [{'l1': 456, 'l2': 'baz'}],
            't': [789, {'t1': dt2, 't2': 'x'}]
        })
        self.assertDictEqual(f.get(), {
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [id1, 'bar']
            },
            'l': [{'l1': 456, 'l2': 'baz'}],
            't': [789, {'t1': dt2, 't2': 'x'}],
        })
        self.assertDictEqual(f.get('d.d1', 'd.d3', 't.1', date_format='iso', as_json=True), {
            'd': {
                'd3': [str(id1), 'bar'],
                'd1': dt1.replace(microsecond=0).isoformat()},
            't': [{'t1': dt2.replace(microsecond=0).isoformat(), 't2': 'x'}]
        })

        self.assertDictEqual(f['d'].value, {'d1': dt1, 'd2': ['foo'], 'd3': [id1, 'bar']})
        self.assertDictEqual(f['d'].self_value, {'d1': dt1, 'd2': ['foo'], 'd3': [id1, 'bar']})
        self.assertDictEqual(f['d'].get(), {'d1': dt1, 'd2': ['foo'], 'd3': [id1, 'bar']})

        self.assertEqual(f['l'].value, [{'l2': 'baz', 'l1': 456}])
        self.assertEqual(f['l'].self_value, [{'l2': 'baz', 'l1': 456}])
        self.assertEqual(f['l'].get(), [{'l2': 'baz', 'l1': 456}])

        self.assertEqual(f['t'].value, [789, {'t1': dt2, 't2': 'x'}])
        self.assertEqual(f['t'].self_value, [789, {'t1': dt2, 't2': 'x'}])
        self.assertEqual(f['t'].get(), [789, {'t1': dt2, 't2': 'x'}])

        self.assertEqual(f.get('l', 't'),
                         {'l': [{'l1': 456, 'l2': 'baz'}],
                          't': [789, {'t1': dt2, 't2': 'x'}]})
        self.assertEqual(f.get('d.d3', 'd.d1', 't.1.t1'),
                         {'d': {'d1': dt1, 'd3': [id1, 'bar']},
                          't': [{'t1': dt2}]})
        self.assertEqual(f['d'].get('d1', 'd2'), {'d1': dt1, 'd2': ['foo']})

        f['d.d1'] = dt2
        f['d.d2'].append('abc')
        f['d.d3.1'] = 'xyz'
        f['l'].append({'l1': 100, 'l2': 100})
        f['t']['1.t1'] = dt1
        self.assertDictEqual(f.value, {
            'd': {
                'd1': dt2,
                'd2': ['foo', 'abc'],
                'd3': [id1, 'xyz']
            },
            'l': [{'l1': 456, 'l2': 'baz'}, {'l1': 100, 'l2': '100'}],
            't': [789, {'t1': dt1, 't2': 'x'}],
        })
        self.assertDictEqual(f.self_value, {
            'd': {
                'd1': dt2,
                'd2': ['foo', 'abc'],
                'd3': [id1, 'xyz']
            },
            'l': [{'l1': 456, 'l2': 'baz'}, {'l1': 100, 'l2': '100'}],
            't': [789, {'t1': dt1, 't2': 'x'}],
        })

        self.assertDictEqual(f.get('d', 'l.1', 't.1.t1', as_json=True, date_format='iso'), {
            'd': {
                'd2': ['foo', 'abc'],
                'd3': [str(id1), 'xyz'],
                'd1': dt2.replace(microsecond=0).isoformat()
            },
            'l': [{'l2': '100', 'l1': 100}],
            't': [{'t1': dt1.replace(microsecond=0).isoformat()}]
        })

    def test_dict_field_3(self):
        dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
        dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
        id1 = ObjectId()
        data = {
            'd': {
                'd1': datetime.datetime,
                'd2': [str],
                'd3': (ObjectId, str)
            },
            'l': [{'l1': int, 'l2': str}],
            't': (int, {'t1': datetime.datetime, 't2': str}),
        }
        f = Field.make(data)

        f.set({
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [id1, 'bar']
            },
            'l': [{'l1': 456, 'l2': 'baz1'}, {'l1': 123, 'l2': 'baz2'}],
            't': [789, {'t1': dt2, 't2': 'x'}],
        })
        self.assertDictEqual(f.value, {
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [id1, 'bar']
            },
            'l': [{'l2': 'baz1', 'l1': 456}, {'l2': 'baz2', 'l1': 123}],
            't': [789, {'t2': 'x', 't1': dt2}],
        })
        self.assertDictEqual(f.self_value, {
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [id1, 'bar']
            },
            'l': [{'l2': 'baz1', 'l1': 456}, {'l2': 'baz2', 'l1': 123}],
            't': [789, {'t2': 'x', 't1': dt2}],
        })

        f.clear()
        f.set({
            'd': {
                'd1': dt1.isoformat(),
                'd2': ['foo'],
                'd3': [str(id1), 'bar']
            },
            'l': [{'l1': 456, 'l2': 'baz1'}, {'l1': 123, 'l2': 'baz2'}],
            't': [789, {'t1': dt2.isoformat(), 't2': 'x'}],
        })
        self.assertDictEqual(f.value, {
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [id1, 'bar']
            },
            'l': [{'l1': 456, 'l2': 'baz1'}, {'l1': 123, 'l2': 'baz2'}],
            't': [789, {'t2': 'x', 't1': dt2}],
        })
        self.assertDictEqual(f.self_value, {
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [id1, 'bar']
            },
            'l': [{'l1': 456, 'l2': 'baz1'}, {'l1': 123, 'l2': 'baz2'}],
            't': [789, {'t2': 'x', 't1': dt2}],
        })

        f.clear()
        f.set({
            'd.d1': dt1.isoformat(),
            'd.d2.1': 'foo',
            'd.d2.2': 'bar',
            'd.d2.0': 'baz',
            'd.d3.1': 'xxx',
            'd.d3.0': str(id1),
            'l.1.l1': 456,
            'l.1.l2': 'baz2',
            'l.0.l1': 123,
            'l.0.l2': 'baz1',
            't.1.t1': dt2.isoformat(),
            't.0': 789
        })
        self.assertDictEqual(f.value, {
            'd': {
                'd1': dt1,
                'd2': ['baz', 'foo', 'bar'],
                'd3': [id1, 'xxx']
            },
            'l': [{'l1': 123, 'l2': 'baz1'}, {'l1': 456, 'l2': 'baz2'}],
            't': [789, {'t2': None, 't1': dt2}]
        })
        self.assertDictEqual(f.self_value, {
            'd': {
                'd1': dt1,
                'd2': ['baz', 'foo', 'bar'],
                'd3': [id1, 'xxx']
            },
            'l': [{'l1': 123, 'l2': 'baz1'}, {'l1': 456, 'l2': 'baz2'}],
            't': [789, {'t2': None, 't1': dt2}]
        })

    def test_dict_field_4(self):
        ch1 = ['a', 'b']
        ch2 = {'x': 1, 'y': 2}
        data = {
            's': ChoiceField(ch1),
            'l': [ChoiceField(ch2)],
            't': (int, ChoiceField(ch2)),
        }
        f = Field.make(data)
        f['s'] = 'a'
        f['l'].append(1)
        f['t'] = [123, 2]

        self.assertDictEqual(f.value, {'s': 'a', 'l': ['x'], 't': [123, 'y']})
        self.assertDictEqual(f.self_value, {'s': 'a', 'l': ['x'], 't': [123, 'y']})
        self.assertDictEqual(f.get(), {'s': 'a', 'l': [1], 't': [123, 2]})

    def test_field_query_1(self):
        f = Field.make([str])

        self.assertDictEqual(f.query, {})
        f.append('foo')
        self.assertDictEqual(f.query, {'$set': ['foo']})
        f.append('bar')
        self.assertDictEqual(f.query, {'$set': ['foo', 'bar']})
        del f[0]
        self.assertDictEqual(f.query, {'$set': ['bar']})
        f.dirty_clear()
        self.assertDictEqual(f.query, {})
        f[1] = 'x'
        self.assertDictEqual(f.query, {'$set': ['bar', 'x']})

    def test_field_query_2(self):
        f = Field.make([{'a': int, 'b': str}])
        self.assertDictEqual(f.query, {})
        f.append({'a': 1})
        self.assertDictEqual(f.query, {'$set': [{'a': 1, 'b': None}]})
        f.append({'b': 'foo'})
        self.assertDictEqual(f.query, {'$set': [{'a': 1, 'b': None}, {'a': None, 'b': 'foo'}]})
        f[0] = {'a': 123, 'b': 'foo'}
        self.assertDictEqual(f.query, {'$set': [{'a': 123, 'b': 'foo'}, {'a': None, 'b': 'foo'}]})

    def test_field_query_3(self):
        f = Field.make([{}])
        self.assertDictEqual(f.query, {})
        f.append({'a': 1})
        self.assertDictEqual(f.query, {'$set': [{'a': 1}]})
        f.append({'b': 'foo'})
        self.assertDictEqual(f.query, {'$set': [{'a': 1}, {'b': 'foo'}]})
        f[0] = {'a': 123, 'b': 'foo'}
        self.assertDictEqual(f.query, {'$set': [{'a': 123, 'b': 'foo'}, {'b': 'foo'}]})

    def test_field_query_4(self):
        f = Field.make((int, str))
        self.assertDictEqual(f.query, {})
        f[1] = 'x'
        self.assertDictEqual(f.query, {'$set': [None, 'x']})
        f[0] = 123
        self.assertDictEqual(f.query, {'$set': [123, 'x']})
        f.set((123, 'x'))
        self.assertDictEqual(f.query, {'$set': [123, 'x']})
        f.set((456, 'foo'))
        self.assertDictEqual(f.query, {'$set': [456, 'foo']})
        del f[0]
        self.assertDictEqual(f.query, {'$set': [None, 'foo']})
        f.dirty_clear()
        self.assertDictEqual(f.query, {})
        f[0] = 123
        self.assertDictEqual(f.query, {'$set': [123, 'foo']})

    def test_field_query_5(self):
        f = Field.make((int, {'a': int}))
        self.assertDictEqual(f.query, {})
        f['1.a'] = 123
        self.assertDictEqual(f.query, {'$set': [None, {'a': 123}]})
        f[0] = 123
        self.assertDictEqual(f.query, {'$set': [123, {'a': 123}]})

    def test_field_query_6(self):
        data = {
            'd1': int,
            'd2': [str],
            'd3': (int, str),
            'd4': {
                'dd1': int,
                'dd2': [str],
                'dd3': (int, str)
            },
            'd5': {}
        }
        f = Field.make(data)
        self.assertDictEqual(f.query, {})
        f['d1'] = 123
        self.assertDictEqual(f.query, {'$set': {'d1': 123}})
        f['d2.0'] = 123
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['123']
        }})
        f['d2'][1] = 'foo'
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['123', 'foo']
        }})
        f['d2'].append('bar')
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['123', 'foo', 'bar']
        }})
        f['d2'].set(['z', 123])
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar']
        }})
        f['d3.0'] = 123
        f['d3.1'] = 123
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [123, '123']
        }})
        f['d3'] = [None, 'foo']
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo']
        }})
        f['d4.dd1'] = 456
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456
        }})
        f['d4.dd2'].append('bar')
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456,
            'd4.dd2': ['bar']
        }})
        f['d4.dd2.2'] = 'x'
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456,
            'd4.dd2': ['bar', None, 'x']
        }})
        f['d4.dd3.1'] = 456
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456,
            'd4.dd2': ['bar', None, 'x'],
            'd4.dd3': [None, '456']
        }})
        f.dirty_clear()
        self.assertDictEqual(f.query, {})
        f.set({
            'd1': 456,
            'd2': ['foo', 'bar'],
            'd3': [123, 'x'],
            'd4': {
                'dd1': 123,
                'dd2': ['a', 'b', 'c'],
                'dd3': [None, None]
            }
        })
        self.assertDictEqual(f.query, {'$set': {
            'd1': 456,
            'd2': ['foo', 'bar', 'bar'],
            'd3': [123, 'x'],
            'd4.dd1': 123,
            'd4.dd2': ['a', 'b', 'c'],
            'd4.dd3': [None, None]
        }})
        f['d5'] = {'a': 1, 'b': 'foo'}
        self.assertDictEqual(f.query, {'$set': {
            'd1': 456,
            'd2': ['foo', 'bar', 'bar'],
            'd3': [123, 'x'],
            'd4.dd1': 123,
            'd4.dd2': ['a', 'b', 'c'],
            'd4.dd3': [None, None],
            'd5': {'a': 1, 'b': 'foo'}
        }})
        f['d4.dd3.1'] = 123
        self.assertDictEqual(f.query, {'$set': {
            'd1': 456,
            'd2': ['foo', 'bar', 'bar'],
            'd3': [123, 'x'],
            'd4.dd1': 123,
            'd4.dd2': ['a', 'b', 'c'],
            'd4.dd3': [None, '123'],
            'd5': {'a': 1, 'b': 'foo'}
        }})

    def test_field_query_7(self):
        f = Field.make({})
        self.assertDictEqual(f.query, {})
        f.set({
            'd1': 456,
            'd2': ['foo', 'bar'],
            'd3': [123],
            'd4': {
                'dd1': 123,
                'dd2': ['a', 'b', 'c'],
                'dd3': [None, None]
            }
        })
        self.assertDictEqual(f.query, {'$set': {
            'd1': 456,
            'd2': ['foo', 'bar'],
            'd3': [123],
            'd4': {
                'dd1': 123,
                'dd2': ['a', 'b', 'c'],
                'dd3': [None, None]
            }
        }})

    def test_field_query_8(self):
        f = Field.make([str])
        f.set(['foo', 'bar'])
        f.dirty_clear()
        f.set(['foo', 'bar'])
        self.assertFalse(f.dirty)
        self.assertEqual(f.query, {})
        f.set(['foo', 'bar1'])
        self.assertTrue(f.dirty)
        self.assertDictEqual(f.query, {'$set': ['foo', 'bar1']})
