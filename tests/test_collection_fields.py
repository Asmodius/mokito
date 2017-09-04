import unittest
import datetime

from bson import ObjectId

from mokito.fields import (
    IntField,
    FloatField,
    StringField,
    BooleanField,
    ObjectIdField,
    DateTimeField,
    ChoiceField
)
from mokito.tools import make_field
from mokito.collections import ListField, TupleField, DictField


class TestCollectionFields(unittest.TestCase):
    # def test_list_field_1(self):
    #     f = make_field([int])
    #     self.assertIsInstance(f, ListField)
    #     self.assertIsInstance(f._rules, IntField)
    #
    #     f = make_field([float])
    #     self.assertIsInstance(f, ListField)
    #     self.assertIsInstance(f._rules, FloatField)
    #
    #     f = make_field([str])
    #     self.assertIsInstance(f, ListField)
    #     self.assertIsInstance(f._rules, StringField)
    #
    #     f = make_field([bool])
    #     self.assertIsInstance(f, ListField)
    #     self.assertIsInstance(f._rules, BooleanField)
    #
    #     f = make_field([datetime.datetime])
    #     self.assertIsInstance(f, ListField)
    #     self.assertIsInstance(f._rules, DateTimeField)
    #
    #     f = make_field([ObjectId])
    #     self.assertIsInstance(f, ListField)
    #     self.assertIsInstance(f._rules, ObjectIdField)
    #
    # def test_list_field_2(self):
    #     f = make_field([str])
    #     for i in [0, '0']:
    #         x = f[i]
    #         self.assertIsInstance(x, StringField)
    #         self.assertIsNone(x.value)
    #
    #     with self.assertRaises(TypeError):
    #         _ = f['foo']
    #
    #     with self.assertRaises(IndexError):
    #         _ = f['0.0']
    #
    # def test_list_field_3(self):
    #     f = make_field([str])
    #     self.assertEqual(f.value, [])
    #     self.assertEqual(f.self_value, [])
    #
    #     f[1].value = 'foo'
    #     self.assertEqual(f.value, [None, 'foo'])
    #     self.assertEqual(f.self_value, [None, 'foo'])
    #     self.assertTrue(f == f[1]._parent)
    #
    #     f.append_value('bar')
    #     self.assertEqual(f.value, [None, 'foo', 'bar'])
    #     self.assertEqual(f.self_value, [None, 'foo', 'bar'])
    #     self.assertTrue(f == f[2]._parent)
    #
    #     f.append(f[2])
    #     self.assertEqual(f.value, [None, 'foo', 'bar', 'bar'])
    #     self.assertEqual(f.self_value, [None, 'foo', 'bar', 'bar'])
    #     self.assertTrue(f == f[3]._parent)
    #
    #     with self.assertRaises(TypeError):
    #         f.append('xxx')
    #
    #     f['5'] = f[1]
    #     self.assertEqual(f.value, [None, 'foo', 'bar', 'bar', None, 'foo'])
    #     self.assertEqual(f.self_value, [None, 'foo', 'bar', 'bar', None, 'foo'])
    #     self.assertTrue(f == f[5]._parent)
    #
    #     self.assertIsNone(f.pop(0).value)
    #     self.assertEqual(f.value, ['foo', 'bar', 'bar', None, 'foo'])
    #     self.assertEqual(f.self_value, ['foo', 'bar', 'bar', None, 'foo'])
    #
    #     self.assertEqual(f.pop().get_value(), 'foo')
    #     self.assertEqual(f.value, ['foo', 'bar', 'bar'])
    #     self.assertEqual(f.self_value, ['foo', 'bar', 'bar'])
    #
    #     self.assertEqual(f.pop(5).value, None)
    #     self.assertEqual(f.value, ['foo', 'bar', 'bar'])
    #     self.assertEqual(f.self_value, ['foo', 'bar', 'bar'])
    #
    #     del f[0]
    #     self.assertEqual(f.value, ['bar', 'bar'])
    #     self.assertEqual(f.self_value, ['bar', 'bar'])
    #
    #     f.set_value(['x', 'bar', 'y'])
    #     self.assertEqual(f.value, ['bar', 'bar', 'y'])
    #     f.clear()
    #     f.set_value(['x', 'bar', 'y'])
    #     self.assertEqual(f.value, ['x', 'bar', 'y'])
    #     self.assertEqual(f.self_value, ['x', 'bar', 'y'])
    #
    #     f[1].set_value(None)
    #     self.assertEqual(f.value, ['x', None, 'y'])
    #     self.assertEqual(f.self_value, ['x', None, 'y'])
    #
    #     f.value = None
    #     self.assertEqual(f.value, [])
    #     self.assertEqual(f.self_value, [])
    #
    # def test_list_field_4(self):
    #     dt1 = datetime.datetime.utcnow()
    #     dt2 = datetime.datetime(2016, 1, 2, 3, 4, 5)
    #
    #     f = make_field([datetime.datetime])
    #     self.assertEqual(f.value, [])
    #     self.assertEqual(f.self_value, [])
    #
    #     f.set_value([dt1, dt2])
    #     self.assertEqual(f.value, [dt1, dt2])
    #     self.assertEqual(f.self_value, [dt1, dt2])
    #     self.assertEqual(f.get_value(_date_format='iso'),
    #                      [dt1.replace(microsecond=0).isoformat(),
    #                       dt2.replace(microsecond=0).isoformat()])
    #     self.assertEqual(f.get_value(_date_format='%d/%m/%y'),
    #                      [dt1.strftime('%d/%m/%y'), dt2.strftime('%d/%m/%y')])
    #     self.assertTrue(f == f[0]._parent)
    #     self.assertTrue(f == f[1]._parent)
    #
    # def test_tuple_field_1(self):
    #     f = make_field((int, str))
    #     self.assertIsInstance(f, TupleField)
    #     self.assertIsInstance(f._val['0'], IntField)
    #     self.assertTrue(f == f._val['0']._parent)
    #     self.assertIsInstance(f._val['1'], StringField)
    #     self.assertTrue(f == f._val['1']._parent)
    #     self.assertListEqual(f.value, [None, None])
    #
    #     for i in [0, '0']:
    #         self.assertIsNone(f[i].value)
    #         self.assertIsNone(f[i].self_value)
    #
    #     with self.assertRaises(TypeError):
    #         _ = f['a']
    #
    #     for i in ['0.0', 2]:
    #         with self.assertRaises(IndexError):
    #             _ = f[i]
    #
    # def test_tuple_field_2(self):
    #     f = make_field((datetime.datetime, str))
    #
    #     self.assertEqual(f.value, [None, None])
    #     self.assertEqual(f.self_value, [None, None])
    #     self.assertEqual(f.get_value(_date_format='iso'), [None, None])
    #
    #     f[1].value = 123
    #     self.assertEqual(f.value, [None, '123'])
    #     self.assertEqual(f.self_value, [None, '123'])
    #     self.assertTrue(f == f[1]._parent)
    #
    #     dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
    #     f[0].value = dt1
    #     self.assertEqual(f.value, [dt1, '123'])
    #     self.assertEqual(f.self_value, [dt1, '123'])
    #     self.assertEqual(f.get_value(_date_format='iso'), ['2016-01-02T03:04:05', '123'])
    #     self.assertTrue(f == f[0]._parent)
    #
    #     f[1].value = None
    #     self.assertEqual(f.value, [dt1, None])
    #     self.assertEqual(f.self_value, [dt1, None])
    #     self.assertTrue(f == f[1]._parent)
    #
    #     del f[0]
    #     self.assertEqual(f.value, [None, None])
    #     self.assertEqual(f.self_value, [None, None])
    #     self.assertTrue(f == f[0]._parent)
    #
    #     f.set_value([dt1, 456])
    #     self.assertEqual(f.value, [dt1, '456'])
    #     self.assertEqual(f.self_value, [dt1, '456'])
    #     self.assertEqual(f.get_value(_date_format='%d/%m/%y'), [dt1.strftime('%d/%m/%y'), '456'])
    #     self.assertTrue(f == f[0]._parent)
    #     self.assertTrue(f == f[1]._parent)
    #
    # def test_dict_field_1(self):
    #     dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
    #     dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
    #     id1 = ObjectId()
    #     data = {
    #         'd': {
    #             'd1': datetime.datetime,
    #             'd2': [str],
    #             'd3': (ObjectId, str)
    #         },
    #         'l': [{'l1': int, 'l2': str}],
    #         't': (int, {'t1': datetime.datetime, 't2': str}),
    #     }
    #     f = make_field(data)
    #
    #     self.assertIsInstance(f, DictField)
    #     self.assertDictEqual(f.value, {
    #         'd': {'d1': None, 'd2': [], 'd3': [None, None]},
    #         'l': [],
    #         't': [None, {'t1': None, 't2': None}],
    #     })
    #     self.assertDictEqual(f.self_value, {
    #         'd': {'d1': None, 'd2': [], 'd3': [None, None]},
    #         'l': [],
    #         't': [None, {'t1': None, 't2': None}],
    #     })
    #     self.assertTrue(f == f['d']._parent)
    #     self.assertTrue(f == f['d']['d1']._parent._parent)
    #     self.assertTrue(f == f['d']['d2']._parent._parent)
    #     self.assertTrue(f == f['d']['d3']._parent._parent)
    #     self.assertTrue(f == f['d']['d3'][0]._parent._parent._parent)
    #     self.assertTrue(f == f['d']['d3'][1]._parent._parent._parent)
    #     self.assertTrue(f == f['l']._parent)
    #     self.assertTrue(f == f['t']._parent)
    #     self.assertTrue(f == f['t'][0]._parent._parent)
    #     self.assertTrue(f == f['t'][1]._parent._parent)
    #
    #     self.assertIsInstance(f._val['d'], DictField)
    #     self.assertIsInstance(f['d'], DictField)
    #     self.assertDictEqual(f['d'].value, {'d1': None, 'd2': [], 'd3': [None, None]})
    #     self.assertDictEqual(f['d'].self_value, {'d1': None, 'd2': [], 'd3': [None, None]})
    #
    #     self.assertIsInstance(f._val['l'], ListField)
    #     self.assertIsInstance(f['l'], ListField)
    #     self.assertEqual(f['l'].value, [])
    #     self.assertEqual(f['l'].self_value, [])
    #
    #     self.assertIsInstance(f._val['t'], TupleField)
    #     self.assertIsInstance(f['t'], TupleField)
    #     self.assertEqual(f['t'].value, [None, {'t1': None, 't2': None}])
    #     self.assertEqual(f['t'].self_value, [None, {'t1': None, 't2': None}])
    #
    #     f.set_value({
    #         'd': {
    #             'd1': dt1,
    #             'd2': ['foo'],
    #             'd3': (id1, 'bar')
    #         },
    #         'l': [{'l1': 456, 'l2': 'baz'}],
    #         't': (789, {'t1': dt2, 't2': 'x'})
    #     })
    #     self.assertTrue(f == f['d']._parent)
    #     self.assertTrue(f == f['d']['d1']._parent._parent)
    #     self.assertTrue(f == f['d']['d2']._parent._parent)
    #     self.assertTrue(f == f['d']['d3']._parent._parent)
    #     self.assertTrue(f == f['d']['d3'][0]._parent._parent._parent)
    #     self.assertTrue(f == f['d']['d3'][1]._parent._parent._parent)
    #     self.assertTrue(f == f['l']._parent)
    #     self.assertTrue(f == f['l'][0]._parent._parent)
    #     self.assertTrue(f == f['l'][0]['l1']._parent._parent._parent)
    #     self.assertTrue(f == f['l'][0]['l2']._parent._parent._parent)
    #     self.assertTrue(f == f['t']._parent)
    #     self.assertTrue(f == f['t'][0]._parent._parent)
    #     self.assertTrue(f == f['t'][1]._parent._parent)
    #     self.assertTrue(f == f['t'][1]['t1']._parent._parent._parent)
    #     self.assertTrue(f == f['t'][1]['t2']._parent._parent._parent)
    #
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': dt1,
    #             'd2': ['foo'],
    #             'd3': [id1, 'bar']
    #         },
    #         'l': [{'l1': 456, 'l2': 'baz'}],
    #         't': [789, {'t1': dt2, 't2': 'x'}]
    #     })
    #     self.assertDictEqual(f.self_value, {
    #         'd': {
    #             'd1': dt1,
    #             'd2': ['foo'],
    #             'd3': [id1, 'bar']
    #         },
    #         'l': [{'l1': 456, 'l2': 'baz'}],
    #         't': [789, {'t1': dt2, 't2': 'x'}]
    #     })
    #     self.assertDictEqual(f.get_value(_date_format='iso', _format='json'), {
    #         'd': {
    #             'd1': dt1.replace(microsecond=0).isoformat(),
    #             'd2': ['foo'],
    #             'd3': [str(id1), 'bar']
    #         },
    #         'l': [{'l1': 456, 'l2': 'baz'}],
    #         't': [789, {'t1': dt2.replace(microsecond=0).isoformat(), 't2': 'x'}],
    #     })
    #
    #     self.assertDictEqual(f['d'].value, {'d1': dt1, 'd2': ['foo'], 'd3': [id1, 'bar']})
    #     self.assertDictEqual(f['d'].self_value, {'d1': dt1, 'd2': ['foo'], 'd3': [id1, 'bar']})
    #
    #     self.assertEqual(f['l'].value, [{'l2': 'baz', 'l1': 456}])
    #     self.assertEqual(f['l'].self_value, [{'l2': 'baz', 'l1': 456}])
    #
    #     self.assertEqual(f['t'].value, [789, {'t1': dt2, 't2': 'x'}])
    #     self.assertEqual(f['t'].self_value, [789, {'t1': dt2, 't2': 'x'}])
    #
    #     f['d.d1'].value = dt2
    #     f['d.d2'].append_value('abc')
    #     f['d.d3.1'].value = 'xyz'
    #     f['l'].append_value({'l1': 100, 'l2': 100})
    #     f['t']['1.t1'].value = dt1
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': dt2,
    #             'd2': ['foo', 'abc'],
    #             'd3': [id1, 'xyz']
    #         },
    #         'l': [{'l1': 456, 'l2': 'baz'}, {'l1': 100, 'l2': '100'}],
    #         't': [789, {'t1': dt1, 't2': 'x'}],
    #     })
    #     self.assertDictEqual(f.self_value, {
    #         'd': {
    #             'd1': dt2,
    #             'd2': ['foo', 'abc'],
    #             'd3': [id1, 'xyz']
    #         },
    #         'l': [{'l1': 456, 'l2': 'baz'}, {'l1': 100, 'l2': '100'}],
    #         't': [789, {'t1': dt1, 't2': 'x'}],
    #     })
    #
    #     f.clear()
    #     self.assertDictEqual(f.value, {
    #         'd': {'d1': None, 'd2': [], 'd3': [None, None]},
    #         'l': [],
    #         't': [None, {'t1': None, 't2': None}],
    #     })
    #
    #     f.set_value({
    #         'd.d1': dt1.isoformat(),
    #         'd.d2.1': 'foo',
    #         'd.d2.2': 'bar',
    #         'd.d2.0': 'baz',
    #         'd.d3.1': 'xxx',
    #         'd.d3.0': str(id1),
    #         'l.1.l1': 456,
    #         'l.1.l2': 'baz2',
    #         'l.0.l1': 123,
    #         'l.0.l2': 'baz1',
    #         't.1.t1': dt2.isoformat(),
    #         't.0': 789
    #     })
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': dt1,
    #             'd2': ['baz', 'foo', 'bar'],
    #             'd3': [id1, 'xxx']
    #         },
    #         'l': [{'l1': 123, 'l2': 'baz1'}, {'l1': 456, 'l2': 'baz2'}],
    #         't': [789, {'t1': dt2, 't2': None}],
    #     })
    #
    #     del f['d.d1']
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': None,
    #             'd2': ['baz', 'foo', 'bar'],
    #             'd3': [id1, 'xxx']
    #         },
    #         'l': [{'l1': 123, 'l2': 'baz1'}, {'l1': 456, 'l2': 'baz2'}],
    #         't': [789, {'t1': dt2, 't2': None}],
    #     })
    #
    #     del f['d']
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': None,
    #             'd2': [],
    #             'd3': [None, None]
    #         },
    #         'l': [{'l1': 123, 'l2': 'baz1'}, {'l1': 456, 'l2': 'baz2'}],
    #         't': [789, {'t1': dt2, 't2': None}],
    #     })
    #
    #     del f['l.1.l2']
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': None,
    #             'd2': [],
    #             'd3': [None, None]
    #         },
    #         'l': [{'l1': 123, 'l2': 'baz1'}, {'l1': 456, 'l2': None}],
    #         't': [789, {'t1': dt2, 't2': None}],
    #     })
    #
    #     del f['l.1']
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': None,
    #             'd2': [],
    #             'd3': [None, None]
    #         },
    #         'l': [{'l1': 123, 'l2': 'baz1'}],
    #         't': [789, {'t1': dt2, 't2': None}],
    #     })
    #
    #     del f['l']
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': None,
    #             'd2': [],
    #             'd3': [None, None]
    #         },
    #         'l': [],
    #         't': [789, {'t1': dt2, 't2': None}],
    #     })
    #
    #     del f['t.1']
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': None,
    #             'd2': [],
    #             'd3': [None, None]
    #         },
    #         'l': [],
    #         't': [789, {'t1': None, 't2': None}],
    #     })
    #
    #     del f['t.0']
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': None,
    #             'd2': [],
    #             'd3': [None, None]
    #         },
    #         'l': [],
    #         't': [None, {'t1': None, 't2': None}],
    #     })
    #
    #     del f['t.1.t1']
    #     self.assertDictEqual(f.value, {
    #         'd': {
    #             'd1': None,
    #             'd2': [],
    #             'd3': [None, None]
    #         },
    #         'l': [],
    #         't': [None, {'t1': None, 't2': None}],
    #     })
    #
    #     with self.assertRaises(IndexError):
    #         del f['t.2']
    #
    #     with self.assertRaises(KeyError):
    #         del f['foo']
    #
    # def test_dict_field_2(self):
    #     ch1 = ['a', 'b']
    #     ch2 = {1: 'x', 2: 'y'}
    #     data = {
    #         's': ChoiceField(ch1),
    #         'l': [ChoiceField(ch2)],
    #         't': (int, ChoiceField(ch2)),
    #     }
    #     f = make_field(data)
    #     f['s'].value = 'a'
    #     f['l'].append_value('x')
    #     f['t'].value = [123, 'y']
    #
    #     self.assertDictEqual(f.value, {'s': 'a', 'l': ['x'], 't': [123, 'y']})
    #     self.assertDictEqual(f.get_value(inner=True), {'s': 'a', 'l': [1], 't': [123, 2]})
    #     self.assertDictEqual(f.self_value, {'s': 'a', 'l': [1], 't': [123, 2]})
    #
    # def test_list_query_1(self):
    #     f = make_field([str])
    #     self.assertDictEqual(f.query, {})
    #     f.append_value('foo')
    #     self.assertDictEqual(f.query, {'$set': ['foo']})
    #     f.append_value('bar')
    #     self.assertDictEqual(f.query, {'$set': ['foo', 'bar']})
    #     del f[0]
    #     self.assertDictEqual(f.query, {'$set': ['bar']})
    #     f.dirty_clear()
    #     self.assertDictEqual(f.query, {})
    #     f[1].value = 'x'
    #     self.assertDictEqual(f.query, {'$set': ['bar', 'x']})
    #     f.pop()
    #     self.assertDictEqual(f.query, {'$set': ['bar']})
    #     f.dirty_clear()
    #
    #     del f[0]
    #     self.assertDictEqual(f.query, {'$set': []})
    #
    # def test_list_query_2(self):
    #     f = make_field([{'a': int, 'b': str}])
    #     self.assertDictEqual(f.query, {})
    #     f.append_value({'a': 1})
    #     self.assertDictEqual(f.query, {'$set': [{'a': 1, 'b': None}]})
    #     f.append_value({'b': 'foo'})
    #     self.assertDictEqual(f.query, {'$set': [{'a': 1, 'b': None}, {'a': None, 'b': 'foo'}]})
    #     f[0].value = {'a': 123, 'b': 'foo'}
    #     self.assertDictEqual(f.query, {'$set': [{'a': 123, 'b': 'foo'}, {'a': None, 'b': 'foo'}]})
    #
    # def test_list_query_3(self):
    #     f = make_field([{}])
    #     self.assertDictEqual(f.query, {})
    #     f.append_value({'a': 1})
    #     self.assertDictEqual(f.query, {'$set': [{'a': 1}]})
    #     f.append_value({'b': 'foo'})
    #     self.assertDictEqual(f.query, {'$set': [{'a': 1}, {'b': 'foo'}]})
    #     f[0].value = {'x': 123, 'y': 'foo'}
    #     self.assertDictEqual(f.query, {'$set': [{'a': 1, 'y': 'foo', 'x': 123}, {'b': 'foo'}]})
    #
    # def test_tuple_query_1(self):
    #     f = make_field((int, str))
    #     self.assertDictEqual(f.query, {})
    #     f[0].value = 123
    #     self.assertDictEqual(f.query, {'$set': [123, None]})
    #     f[1].value = 'foo'
    #     self.assertDictEqual(f.query, {'$set': [123, 'foo']})
    #     f.dirty_clear()
    #     self.assertDictEqual(f.query, {})
    #     del f[0]
    #     self.assertDictEqual(f.query, {'$set': [None, 'foo']})
    #
    # def test_tuple_query_2(self):
    #     f = make_field((str, [int]))
    #     self.assertDictEqual(f.query, {})
    #     f.set_value(['foo', [1]])
    #     self.assertDictEqual(f.query, {'$set': ['foo', [1]]})
    #     f['1.2'].value = 123
    #     self.assertDictEqual(f.query, {'$set': ['foo', [1, None, 123]]})
    #
    # def test_tuple_query_3(self):
    #     f = make_field((int, {'a': int}))
    #     self.assertDictEqual(f.query, {})
    #     f['1.a'].value = 123
    #     self.assertDictEqual(f.query, {'$set': [None, {'a': 123}]})
    #     f[0].value = 123
    #     self.assertDictEqual(f.query, {'$set': [123, {'a': 123}]})

    def test_dict_query_1(self):
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
        f = make_field(data)
        self.assertDictEqual(f.query, {})
        f['d1'].value = 123
        print('---1', f.dirty_fields)

        self.assertDictEqual(f.query, {'$set': {'d1': 123}})
        print('---1', f.dirty_fields)
        f['d2.0'].value = 123
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['123']
        }})
        f['d2'][1].value = 'foo'
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['123', 'foo']
        }})
        f['d2'].append_value('bar')
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['123', 'foo', 'bar']
        }})
        f['d2'].set_value(['z', 123])
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar']
        }})
        f['d3.0'].value = 123
        f['d3.1'].value = 123
        print('---3', f.dirty_fields)
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [123, '123']
        }})
        f['d3'].value = [None, 'foo']
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo']
        }})
        f['d4.dd1'].value = 456
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456
        }})
        f['d4.dd2'].append_value('bar')
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456,
            'd4.dd2': ['bar']
        }})
        f['d4.dd2.2'].value = 'x'
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456,
            'd4.dd2': ['bar', None, 'x']
        }})
        f['d4.dd3.1'].value = 456
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456,
            'd4.dd2': ['bar', None, 'x'],
            'd4.dd3': [None, '456']
        }})
        print('---4', f.dirty_fields)
        f.dirty_clear()
        self.assertDictEqual(f.query, {})
        f.set_value({
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
        f['d5'].value = {'a': 1, 'b': 'foo'}
        print('---5', f.dirty_fields)
        self.assertDictEqual(f.query, {'$set': {
            'd1': 456,
            'd2': ['foo', 'bar', 'bar'],
            'd3': [123, 'x'],
            'd4.dd1': 123,
            'd4.dd2': ['a', 'b', 'c'],
            'd4.dd3': [None, None],
            'd5': {'a': 1, 'b': 'foo'}
        }})

        f['d4.dd3.1'].value = 123
        self.assertDictEqual(f.query, {'$set': {
            'd1': 456,
            'd2': ['foo', 'bar', 'bar'],
            'd3': [123, 'x'],
            'd4.dd1': 123,
            'd4.dd2': ['a', 'b', 'c'],
            'd4.dd3': [None, '123'],
            'd5': {'a': 1, 'b': 'foo'}
        }})

    # def test_dict_query_2(self):
    #     f = make_field({})
    #     self.assertDictEqual(f.query, {})
    #     f.set_value({
    #         'd1': 456,
    #         'd2': ['foo', 'bar'],
    #         'd3': [123],
    #         'd4': {
    #             'dd1': 123,
    #             'dd2': ['a', 'b', 'c'],
    #         }
    #     })
    #     self.assertDictEqual(f.query, {'$set': {
    #         'd1': 456,
    #         'd2': ['foo', 'bar'],
    #         'd3': [123],
    #         'd4': {
    #             'dd1': 123,
    #             'dd2': ['a', 'b', 'c'],
    #         }
    #     }})
