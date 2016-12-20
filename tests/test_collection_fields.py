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
        self.assertEqual(f.get(), [])
        self.assertEqual(f.get(flat=True), {})

        f[1] = 'foo'
        self.assertEqual(f.value, [None, 'foo'])
        self.assertEqual(f.get(), [None, 'foo'])
        self.assertDictEqual(f.get(flat=True), {'0': None, '1': 'foo'})

        f.append('bar')
        self.assertEqual(f.value, [None, 'foo', 'bar'])
        self.assertEqual(f.get(), [None, 'foo', 'bar'])
        self.assertDictEqual(f.get(flat=True), {'0': None, '1': 'foo', '2': 'bar'})

        f['3'] = 'x'
        self.assertEqual(f.value, [None, 'foo', 'bar', 'x'])
        self.assertEqual(f.get(), [None, 'foo', 'bar', 'x'])
        self.assertDictEqual(f.get(flat=True), {'0': None, '1': 'foo', '2': 'bar', '3': 'x'})

        self.assertIsNone(f.pop(0).get())
        self.assertEqual(f.value, ['foo', 'bar', 'x'])
        self.assertEqual(f.get(), ['foo', 'bar', 'x'])
        self.assertDictEqual(f.get(flat=True), {'0': 'foo', '1': 'bar', '2': 'x'})

        self.assertEqual(f.pop(1).value, 'bar')
        self.assertEqual(f.value, ['foo', 'x'])
        self.assertEqual(f.get(), ['foo', 'x'])
        self.assertDictEqual(f.get(flat=True), {'0': 'foo', '1': 'x'})

        self.assertEqual(f.pop().get(), 'x')
        self.assertEqual(f.value, ['foo'])
        self.assertEqual(f.get(), ['foo'])
        self.assertDictEqual(f.get(flat=True), {'0': 'foo'})

        self.assertEqual(f.pop(3, default=123).get(), '123')
        self.assertEqual(f.value, ['foo'])
        self.assertEqual(f.get(), ['foo'])
        self.assertDictEqual(f.get(flat=True), {'0': 'foo'})

        f[2] = 'zzz'
        self.assertEqual(f.value, ['foo', None, 'zzz'])
        self.assertEqual(f.get(), ['foo', None, 'zzz'])
        self.assertDictEqual(f.get(flat=True), {'0': 'foo', '1': None, '2': 'zzz'})

        del f[0]
        self.assertEqual(f.value, [None, 'zzz'])
        self.assertEqual(f.get(), [None, 'zzz'])
        self.assertDictEqual(f.get(flat=True), {'0': None, '1': 'zzz'})

        f.set(['foo', 'bar'])
        self.assertEqual(f.value, ['foo', 'bar'])
        self.assertEqual(f.get(), ['foo', 'bar'])
        self.assertDictEqual(f.get(flat=True), {'0': 'foo', '1': 'bar'})

        f[1].set(None)
        self.assertEqual(f.value, ['foo', None])
        self.assertEqual(f.get(), ['foo', None])
        self.assertDictEqual(f.get(flat=True), {'0': 'foo', '1': None})
        self.assertDictEqual(f.get(flat=True, aliases={0: 'aaa'}),
                             {'aaa': 'foo', '1': None})

    def test_list_field_4(self):
        dt1 = datetime.datetime.utcnow()
        dt2 = datetime.datetime(2016, 1, 2, 3, 4, 5)

        f = Field.make([datetime.datetime])
        self.assertEqual(f.value, [])
        self.assertEqual(f.get(), [])
        self.assertEqual(f.get(flat=True), {})

        f.set([dt1, dt2])
        self.assertEqual(f.value, [dt1, dt2])
        self.assertEqual(f.get(), [dt1, dt2])
        self.assertDictEqual(f.get(flat=True), {'0': dt1, '1': dt2})
        self.assertEqual(f.get(date_format='iso'),
                         [dt1.replace(microsecond=0).isoformat(),
                          dt2.replace(microsecond=0).isoformat()])
        self.assertEqual(f.get(date_format='%d/%m/%y'),
                         [dt1.strftime('%d/%m/%y'), dt2.strftime('%d/%m/%y')])

        param = {'0.date_format': 'iso', '1.date_format': '%d/%m/%y'}
        self.assertEqual(f.get(**param),
                         [dt1.replace(microsecond=0).isoformat(),
                          dt2.strftime('%d/%m/%y')])

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

        with self.assertRaises(TypeError):
            _ = f['0.0']

        with self.assertRaises(IndexError):
            _ = f['a']

        with self.assertRaises(IndexError):
            _ = f[2]

    def test_field_set_2(self):
        f = Field.make((datetime.datetime, str))

        self.assertEqual(f.value, [None, None])
        self.assertEqual(f.get(), [None, None])
        self.assertDictEqual(f.get(flat=True, date_format='iso'),
                             {'0': None, '1': None})

        f[1] = 123
        self.assertEqual(f.value, [None, '123'])
        self.assertEqual(f.get(), [None, '123'])
        self.assertDictEqual(f.get(flat=True, date_format='iso'),
                             {'0': None, '1': '123'})

        dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
        f[0] = dt1
        self.assertEqual(f.value, [dt1, '123'])
        self.assertEqual(f.get(), [dt1, '123'])
        self.assertDictEqual(f.get(flat=True, date_format='iso'),
                             {'0': '2016-01-02T03:04:05', '1': '123'})

        with self.assertRaises(IndexError):
            f[2] = 'x'

        f[1] = None
        self.assertEqual(f.value, [dt1, None])
        self.assertEqual(f.get(), [dt1, None])
        self.assertDictEqual(f.get(flat=True), {'0': dt1, '1': None})

        del f[0]
        self.assertEqual(f.value, [None, None])
        self.assertEqual(f.get(), [None, None])
        self.assertDictEqual(f.get(flat=True), {'0': None, '1': None})

        f.set([dt1, 456])
        self.assertEqual(f.value, [dt1, '456'])
        self.assertEqual(f.get(), [dt1, '456'])
        self.assertDictEqual(f.get(flat=True, date_format='%d/%m/%y'),
                             {'0': dt1.strftime('%d/%m/%y'), '1': '456'})

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
        _id1 = ObjectId()
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
        self.assertDictEqual(f.get(), {
            'd': {'d1': None, 'd2': [], 'd3': [None, None]},
            'l': [],
            't': [None, {'t1': None, 't2': None}],
        })
        self.assertDictEqual(f.get(flat=True), {
            'd.d1': None,
            'd.d2': {},
            'd.d3.0': None,
            'd.d3.1': None,
            'l': {},
            't.0': None,
            't.1.t1': None,
            't.1.t2': None
        })
        self.assertDictEqual(f.get(flat=True, aliases={
            'd.d1': 'f1',
            'd.d2': 'f2',
            'd.d3.0': 'f3',
            'd.d3.1': 'f4',
            'l': 'f5',
            't.0': 'f6',
            't.1.t1': 'f7',
            't.1.t2': 'f8'
        }), {
            'f1': None,
            'f2': {},
            'f3': None,
            'f4': None,
            'f5': {},
            'f6': None,
            'f7': None,
            'f8': None
        })

        self.assertIsInstance(f._val['d'], DictField)
        self.assertIsInstance(f['d'], DictField)
        self.assertDictEqual(f['d'].value, {'d1': None, 'd2': [], 'd3': [None, None]})
        self.assertDictEqual(f['d'].get(), {'d1': None, 'd2': [], 'd3': [None, None]})
        self.assertDictEqual(f['d'].get(flat=True), {'d1': None, 'd2': {}, 'd3.0': None, 'd3.1': None})

        self.assertIsInstance(f._val['l'], ListField)
        self.assertIsInstance(f['l'], ListField)
        self.assertEqual(f['l'].value, [])
        self.assertEqual(f['l'].get(), [])
        self.assertEqual(f['l'].get(flat=True), {})

        self.assertIsInstance(f._val['t'], TupleField)
        self.assertIsInstance(f['t'], TupleField)
        self.assertEqual(f['t'].value, [None, {'t1': None, 't2': None}])
        self.assertEqual(f['t'].get(), [None, {'t1': None, 't2': None}])
        self.assertEqual(f['t'].get(flat=True), {'0': None, '1.t1': None, '1.t2': None})

        self.assertEqual(f.get(fields=['l', 't']), {'l': [], 't': [None, {'t1': None, 't2': None}]})
        self.assertEqual(f.get(fields=['d.d3', 'd.d1', 't.1.t1']),
                         {'d': {'d1': None, 'd3': [None, None]}, 't': [{'t1': None}]})
        self.assertEqual(f.get(fields=['d.d3', 'd.d1', 't.1.t1'], flat=True),
                         {'d.d1': None, 'd.d3.0': None, 'd.d3.1': None, 't.1.t1': None})
        self.assertEqual(f.get(fields=['d.d3', 'd.d1', 't.1.t1'],
                               aliases={'d.d1': 'f1', 'd.d3.0': 'f2', 'd.d3.1': 'f3', 't.1.t1': 'f4'}, flat=True),
                         {'f1': None, 'f2': None, 'f3': None, 'f4': None})
        self.assertEqual(f['d'].get(fields=['d1', 'd2']), {'d1': None, 'd2': []})
        self.assertEqual(f['d'].get(fields=['d1', 'd2'], aliases={'d1': 'f1', 'd2': 'f2'}),
                         {'f1': None, 'f2': []})

        f.set({
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': (_id1, 'bar')
            },
            'l': [{'l1': 456, 'l2': 'baz'}],
            't': (789, {'t1': dt2, 't2': 'x'}),
        })
        self.assertDictEqual(f.value, {
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [_id1, 'bar']
            },
            'l': [{'l1': 456, 'l2': 'baz'}],
            't': [789, {'t1': dt2, 't2': 'x'}]
        })
        self.assertDictEqual(f.get(flat=True), {
            'd.d1': dt1,
            'd.d2.0': 'foo',
            'd.d3.0': _id1,
            'd.d3.1': 'bar',
            'l.0.l1': 456,
            'l.0.l2': 'baz',
            't.0': 789,
            't.1.t1': dt2,
            't.1.t2': 'x'
        })
        self.assertDictEqual(f.get(flat=True, as_json=True, aliases={
            'd.d1': 'f1',
            'd.d2.0': 'f2',
            'd.d3.0': 'f3',
            'd.d3.1': 'f4',
            'l.0.l2': 'f6',
            'l.0.l1': 'f5',
            't.0': 'f7',
            't.1.t1': 'f8',
            't.1.t2': 'f9'
        }), {
            'f1': dt1,
            'f2': 'foo',
            'f3': str(_id1),
            'f4': 'bar',
            'f5': 456,
            'f6': 'baz',
            'f7': 789,
            'f8': dt2,
            'f9': 'x'
        })
        param = {'t.date_format': 'iso'}
        self.assertDictEqual(f.get(flat=True, **param), {
            'd.d1': dt1,
            'd.d2.0': 'foo',
            'd.d3.0': _id1,
            'd.d3.1': 'bar',
            'l.0.l1': 456,
            'l.0.l2': 'baz',
            't.0': 789,
            't.1.t1': dt2.replace(microsecond=0).isoformat(),
            't.1.t2': 'x'
        })

        self.assertDictEqual(f['d'].value, {'d1': dt1, 'd2': ['foo'], 'd3': [_id1, 'bar']})
        self.assertDictEqual(f['d'].get(flat=True), {'d1': dt1, 'd2.0': 'foo', 'd3.0': _id1, 'd3.1': 'bar'})
        self.assertDictEqual(f['d'].get(flat=True, aliases={'d1': 'f1', 'd2.0': 'f2', 'd3.0': 'f3', 'd3.1': 'f4'}),
                             {'f1': dt1, 'f2': 'foo', 'f3': _id1, 'f4': 'bar'})

        self.assertEqual(f['l'].get(), [{'l2': 'baz', 'l1': 456}])
        self.assertEqual(f['l'].get(flat=True), {'0.l2': 'baz', '0.l1': 456})

        self.assertEqual(f['t'].value, [789, {'t1': dt2, 't2': 'x'}])
        self.assertEqual(f['t'].get(flat=True), {'0': 789, '1.t1': dt2, '1.t2': 'x'})

        self.assertEqual(f.get(fields=['l', 't']),
                         {'l': [{'l1': 456, 'l2': 'baz'}],
                          't': [789, {'t1': dt2, 't2': 'x'}]})
        self.assertEqual(f.get(fields=['d.d3', 'd.d1', 't.1.t1']),
                         {'d': {'d1': dt1, 'd3': [_id1, 'bar']},
                          't': [{'t1': dt2}]})
        self.assertEqual(f.get(fields=['d.d3', 'd.d1', 't.1.t1'], flat=True),
                         {'d.d1': dt1, 'd.d3.0': _id1, 'd.d3.1': 'bar', 't.1.t1': dt2})
        self.assertEqual(f.get(fields=['d.d3', 'd.d1', 't.1.t1'],
                               aliases={'d.d1': 'f1', 'd.d3.0': 'f2', 'd.d3.1': 'f3', 't.1.t1': 'f4'}, flat=True),
                         {'f1': dt1, 'f2': _id1, 'f3': 'bar', 'f4': dt2})
        self.assertEqual(f['d'].get(fields=['d1', 'd2']), {'d1': dt1, 'd2': ['foo']})
        self.assertEqual(f['d'].get(fields=['d1', 'd2'], aliases={'d1': 'f1', 'd2': 'f2'}),
                         {'f1': dt1, 'f2': ['foo']})

        f['d.d1'] = dt2
        f['d.d2'].append('abc')
        f['d.d3.1'] = 'xyz'
        f['l'].append({'l1': 100, 'l2': 100})
        f['t']['1.t1'] = dt1
        self.assertDictEqual(f.value, {
            'd': {
                'd1': dt2,
                'd2': ['foo', 'abc'],
                'd3': [_id1, 'xyz']
            },
            'l': [{'l1': 456, 'l2': 'baz'}, {'l1': 100, 'l2': '100'}],
            't': [789, {'t1': dt1, 't2': 'x'}],
        })
        self.assertDictEqual(f.get(flat=True, as_json=True), {
            'd.d1': dt2,
            'd.d2.0': 'foo',
            'd.d2.1': 'abc',
            'd.d3.0': str(_id1),
            'd.d3.1': 'xyz',

            'l.0.l1': 456,
            'l.0.l2': 'baz',
            'l.1.l1': 100,
            'l.1.l2': '100',

            't.0': 789,
            't.1.t1': dt1,
            't.1.t2': 'x',
        })

    def test_dict_field_3(self):
        dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
        dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
        _id1 = ObjectId()
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
                'd3': [_id1, 'bar']
            },
            'l': [{'l1': 456, 'l2': 'baz1'}, {'l1': 123, 'l2': 'baz2'}],
            't': [789, {'t1': dt2, 't2': 'x'}],
        })
        self.assertDictEqual(f.value, {
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [_id1, 'bar']
            },
            'l': [{'l2': 'baz1', 'l1': 456}, {'l2': 'baz2', 'l1': 123}],
            't': [789, {'t2': 'x', 't1': dt2}],
        })

        f.clear()
        f.set({
            'd': {
                'd1': dt1.isoformat(),
                'd2': ['foo'],
                'd3': [str(_id1), 'bar']
            },
            'l': [{'l1': 456, 'l2': 'baz1'}, {'l1': 123, 'l2': 'baz2'}],
            't': [789, {'t1': dt2.isoformat(), 't2': 'x'}],
        })
        self.assertDictEqual(f.value, {
            'd': {
                'd1': dt1,
                'd2': ['foo'],
                'd3': [_id1, 'bar']
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
            'd.d3.0': str(_id1),
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
                'd3': [_id1, 'xxx']
            },
            'l': [{'l1': 123, 'l2': 'baz1'}, {'l1': 456, 'l2': 'baz2'}],
            't': [789, {'t2': None, 't1': dt2}]
        })

        f.clear()
        f.set({
            'f1': dt1.isoformat(),
            'f2': 'foo',
            'f3': 'bar',
            'f4': 'baz',
            'f5': 'xxx',
            'f6': str(_id1),
            'f7': 456,
            'f8': 'baz2',
            'f9': 123,
            'f10': 'baz1',
            'f11': dt2.isoformat(),
            'f12': 789
        }, aliases={
            'f1': 'd.d1',
            'f2': 'd.d2.1',
            'f3': 'd.d2.2',
            'f4': 'd.d2.0',
            'f5': 'd.d3.1',
            'f6': 'd.d3.0',
            'f7': 'l.1.l1',
            'f8': 'l.1.l2',
            'f9': 'l.0.l1',
            'f10': 'l.0.l2',
            'f11': 't.1.t1',
            'f12': 't.0'
        })
        self.assertDictEqual(f.value, {
            'd': {
                'd1': dt1,
                'd2': ['baz', 'foo', 'bar'],
                'd3': [_id1, 'xxx']
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
        self.assertDictEqual(f.get(), {'s': 'a', 'l': [1], 't': [123, 2]})
        self.assertDictEqual(f.get(flat=True), {'s': 'a', 'l.0': 1, 't.0': 123, 't.1': 2})

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
