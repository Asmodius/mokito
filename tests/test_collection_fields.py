# # coding: utf-8
#
# import unittest
# import datetime
#
# from bson import ObjectId
#
# from mokito.model import (
#     Field,
#     IntField,
#     FloatField,
#     StringField,
#     BooleanField,
#     ObjectIdField,
#     DateTimeField,
#     DictField,
#     TupleField,
#     ListField
# )
#
#
# class TestCollectionFields(unittest.TestCase):
#
#     def test_dict_field_1(self):
#         data = {
#             'f0': None,
#             'f1': IntField,
#             'f2': int,
#             'f3': IntField(),
#             'f4': float,
#             'f5': str,
#             'f6': bool,
#             'f7': datetime.datetime,
#             'f8': ObjectId
#         }
#         f = Field.make(data)
#         self.assertIsInstance(f, DictField)
#         self.assertIsInstance(f._val['f0'], Field)
#         self.assertIsInstance(f._val['f0'], Field)
#         self.assertIsInstance(f._val['f1'], IntField)
#         self.assertIsInstance(f._val['f2'], IntField)
#         self.assertIsInstance(f._val['f3'], IntField)
#         self.assertIsInstance(f._val['f4'], FloatField)
#         self.assertIsInstance(f._val['f5'], StringField)
#         self.assertIsInstance(f._val['f6'], BooleanField)
#         self.assertIsInstance(f._val['f7'], DateTimeField)
#         self.assertIsInstance(f._val['f8'], ObjectIdField)
#
#     def test_list_field_1(self):
#         f = Field.make([None])
#         self.assertIsInstance(f, ListField)
#         self.assertEqual(f._val, {})
#         self.assertIsInstance(f._rules, Field)
#
#         f = Field.make([int])
#         self.assertIsInstance(f, ListField)
#         self.assertEqual(f._val, {})
#         self.assertIsInstance(f._rules, IntField)
#
#         f = Field.make([IntField])
#         self.assertEqual(f._val, {})
#         self.assertIsInstance(f._rules, IntField)
#
#         f = Field.make([float])
#         self.assertIsInstance(f, ListField)
#         self.assertEqual(f._val, {})
#         self.assertIsInstance(f._rules, FloatField)
#
#         f = Field.make([str])
#         self.assertIsInstance(f, ListField)
#         self.assertEqual(f._val, {})
#         self.assertIsInstance(f._rules, StringField)
#
#         f = Field.make([bool])
#         self.assertIsInstance(f, ListField)
#         self.assertEqual(f._val, {})
#         self.assertIsInstance(f._rules, BooleanField)
#
#         f = Field.make([datetime.datetime])
#         self.assertIsInstance(f, ListField)
#         self.assertEqual(f._val, {})
#         self.assertIsInstance(f._rules, DateTimeField)
#
#         f = Field.make([ObjectId])
#         self.assertIsInstance(f, ListField)
#         self.assertEqual(f._val, {})
#         self.assertIsInstance(f._rules, ObjectIdField)
#
#     def test_tuple_field_1(self):
#         data = (None, int, IntField)
#         f = Field.make(data)
#         self.assertIsInstance(f, TupleField)
#         self.assertIsInstance(f._val[0], Field)
#         self.assertIsInstance(f._val[1], IntField)
#         self.assertIsInstance(f._val[2], IntField)
#
#         data = (float, str, bool, ObjectId, datetime.datetime)
#         f = Field.make(data)
#         self.assertIsInstance(f, TupleField)
#         self.assertIsInstance(f._val[0], FloatField)
#         self.assertIsInstance(f._val[1], StringField)
#         self.assertIsInstance(f._val[2], BooleanField)
#         self.assertIsInstance(f._val[3], ObjectIdField)
#         self.assertIsInstance(f._val[4], DateTimeField)
#
#     def test_dict_field_1(self):
#         data = {
#             'd': {
#                 'd1': int,
#                 'd2': [str],
#                 'd3': (int, str)
#             },
#             'l': [{'l1': int, 'l2': str}],
#             't': (int, {'t1': int, 't2': str}),
#         }
#         f = Field.make(data)
#         self.assertIsInstance(f, DictField)
#         self.assertIsInstance(f._val['d'], DictField)
#         self.assertIsInstance(f._val['l'], ListField)
#         self.assertIsInstance(f._val['t'], TupleField)
#
#     def test_field_get_1(self):
#         data = {
#             'd1': int,
#             'd2': [str],
#             'd3': (int, str),
#             'd4': {
#                 'dd1': int,
#                 'dd2': [str],
#                 'dd3': (int, str)
#             }
#         }
#         f = Field.make(data)
#
#         self.assertIsInstance(f['d1'], IntField)
#         self.assertEqual(f['d1'].get(), None)
#         self.assertEqual(f['d1'].value, None)
#
#         self.assertIsInstance(f['d2'], ListField)
#         self.assertEqual(f['d2'].get(), [])
#         self.assertEqual(f['d2'].value, [])
#
#         self.assertIsInstance(f['d3'], TupleField)
#         self.assertEqual(f['d3'].get(), [None, None])
#         self.assertEqual(f['d3'].value, [None, None])
#
#         self.assertIsInstance(f['d4'], DictField)
#         self.assertDictEqual(f['d4'].get(), {'dd1': None, 'dd2': [], 'dd3': [None, None]})
#         self.assertDictEqual(f['d4'].value, {'dd1': None, 'dd2': [], 'dd3': [None, None]})
#         self.assertEqual(f['d4.dd1'].get(), None)
#         self.assertEqual(f['d4.dd1'].value, None)
#         self.assertEqual(f['d4']['dd1'].get(), None)
#         self.assertEqual(f['d4']['dd1'].value, None)
#         self.assertEqual(f['d4.dd2'].get(), [])
#         self.assertEqual(f['d4.dd2'].value, [])
#         self.assertEqual(f['d4']['dd2'].get(), [])
#         self.assertEqual(f['d4']['dd2'].value, [])
#         self.assertEqual(f['d4.dd3'].get(), [None, None])
#         self.assertEqual(f['d4.dd3'].value, [None, None])
#         self.assertEqual(f['d4']['dd3'].get(), [None, None])
#         self.assertEqual(f['d4']['dd3'].value, [None, None])
#
#     def test_field_get_2(self):
#         data = [str]
#         f = Field.make(data)
#
#         for i in [0, '0', '0.0']:
#             with self.assertRaises(IndexError):
#                 _ = f[i]
#
#         with self.assertRaises(ValueError):
#             _ = f['a']
#
#     def test_field_get_3(self):
#         data = (str, int)
#         f = Field.make(data)
#
#         for i in [0, '0']:
#             self.assertIsNone(f[i].value)
#
#         with self.assertRaises(TypeError):
#             _ = f['0.0']
#
#         with self.assertRaises(ValueError):
#             _ = f['a']
#
#         with self.assertRaises(IndexError):
#             _ = f[2]
#
#     def test_field_set_1(self):
#         data = [str]
#         f = Field.make(data)
#
#         self.assertEqual(f.get(), [])
#         self.assertEqual(f.value, [])
#         f[1] = 'foo'
#         self.assertEqual(f.get(), [None, 'foo'])
#         self.assertEqual(f.value, [None, 'foo'])
#         f.append('bar')
#         self.assertEqual(f.get(), [None, 'foo', 'bar'])
#         self.assertEqual(f.value, [None, 'foo', 'bar'])
#         f['3'] = 'x'
#         self.assertEqual(f.get(), [None, 'foo', 'bar', 'x'])
#         self.assertEqual(f.value, [None, 'foo', 'bar', 'x'])
#         self.assertIsNone(f.pop(0).get())
#         self.assertEqual(f.get(), ['foo', 'bar', 'x'])
#         self.assertEqual(f.value, ['foo', 'bar', 'x'])
#         self.assertEqual(f.pop(1).value, 'bar')
#         self.assertEqual(f.get(), ['foo', 'x'])
#         self.assertEqual(f.value, ['foo', 'x'])
#         self.assertEqual(f.pop().get(), 'x')
#         self.assertEqual(f.get(), ['foo'])
#         self.assertEqual(f.value, ['foo'])
#         self.assertEqual(f.pop(3, default=123).get(), '123')
#         self.assertEqual(f.get(), ['foo'])
#         self.assertEqual(f.value, ['foo'])
#         f[2] = 'zzz'
#         self.assertEqual(f.get(), ['foo', None, 'zzz'])
#         self.assertEqual(f.value, ['foo', None, 'zzz'])
#         del f[0]
#         self.assertEqual(f.get(), [None, 'zzz'])
#         self.assertEqual(f.value, [None, 'zzz'])
#         f.set(['foo', 'bar'])
#         self.assertEqual(f.get(), ['foo', 'bar'])
#         self.assertEqual(f.value, ['foo', 'bar'])
#
#     def test_field_set_2(self):
#         data = (int, str)
#         f = Field.make(data)
#
#         self.assertEqual(f.get(), [None, None])
#         self.assertEqual(f.value, [None, None])
#         f[1] = 123
#         self.assertEqual(f.get(), [None, '123'])
#         self.assertEqual(f.value, [None, '123'])
#         f[0] = 456
#         self.assertEqual(f.get(), [456, '123'])
#         self.assertEqual(f.value, [456, '123'])
#         with self.assertRaises(IndexError):
#             f[2] = 'x'
#         f[1] = None
#         self.assertEqual(f.get(), [456, None])
#         self.assertEqual(f.value, [456, None])
#         del f[0]
#         self.assertEqual(f.get(), [None, None])
#         self.assertEqual(f.value, [None, None])
#         f.set([123, 456])
#         self.assertEqual(f.get(), [123, '456'])
#         self.assertEqual(f.value, [123, '456'])
#
#     def test_field_set_3(self):
#         data = {
#             'd1': int,
#             'd2': [str],
#             'd3': (int, str),
#             'd4': {
#                 'dd1': int,
#                 'dd2': [str],
#                 'dd3': (int, str)
#             }
#         }
#         f = Field.make(data)
#
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': None,
#             'd2': [],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d1'] = 123
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': [],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d2.0'] = 123
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['123'],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d2'][1] = 'foo'
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['123', 'foo'],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d2'].append('bar')
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['123', 'foo', 'bar'],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d2'].set(['z', 123])
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d3.0'] = 123
#         f['d3.1'] = 123
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [123, '123'],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d3'] = [None, 'foo']
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd1'] = 456
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd2'].append('bar')
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': ['bar'],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd2.2'] = 'x'
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': ['bar', None, 'x'],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd3.1'] = 456
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': ['bar', None, 'x'],
#                 'dd3': [None, '456']
#             }
#         })
#
#         f.set({
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         })
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         })
#
#     def test_field_set_4(self):
#         data = {}
#         f = Field.make(data)
#
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {})
#
#         f['f1'] = 123
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {'f1': 123})
#
#         f['f2'] = ['foo']
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'f1': 123,
#             'f2': ['foo']
#         })
#
#         f['f3'] = ('bar', 123)
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'f1': 123,
#             'f2': ['foo'],
#             'f3': ['bar', 123]
#         })
#
#         f['f4'] = {'a': 1, 'b': 'foo'}
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'f1': 123,
#             'f2': ['foo'],
#             'f3': ['bar', 123],
#             'f4': {'a': 1, 'b': 'foo'}
#         })
#
#     def test_field_set_5(self):
#         f = Field.make({})
#
#         data = {
#             'f1': 123,
#             'f2': ['foo'],
#             'f3': ('bar', 123),
#             'f4': {'a': 1, 'b': 'foo'}
#         }
#         f.set(data)
#         data['f3'] = list(data['f3'])
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), data)
#
#     def test_field_query_1(self):
#         f = Field.make([str])
#
#         self.assertDictEqual(f.query, {})
#         f.append('foo')
#         self.assertDictEqual(f.query, {'$set': ['foo']})
#         f.append('bar')
#         self.assertDictEqual(f.query, {'$set': ['foo', 'bar']})
#         del f[0]
#         self.assertDictEqual(f.query, {'$set': ['bar']})
#         f.dirty_clear()
#         self.assertDictEqual(f.query, {})
#         f[1] = 'x'
#         self.assertDictEqual(f.query, {'$set': ['bar', 'x']})
#
#     def test_field_query_2(self):
#         f = Field.make([{'a': int, 'b': str}])
#         self.assertDictEqual(f.query, {})
#         f.append({'a': 1})
#         self.assertDictEqual(f.query, {'$set': [{'a': 1, 'b': None}]})
#         f.append({'b': 'foo'})
#         self.assertDictEqual(f.query, {'$set': [{'a': 1, 'b': None}, {'a': None, 'b': 'foo'}]})
#         f[0] = {'a': 123, 'b': 'foo'}
#         self.assertDictEqual(f.query, {'$set': [{'a': 123, 'b': 'foo'}, {'a': None, 'b': 'foo'}]})
#
#     def test_field_query_3(self):
#         f = Field.make([{}])
#         self.assertDictEqual(f.query, {})
#         f.append({'a': 1})
#         self.assertDictEqual(f.query, {'$set': [{'a': 1}]})
#         f.append({'b': 'foo'})
#         self.assertDictEqual(f.query, {'$set': [{'a': 1}, {'b': 'foo'}]})
#         f[0] = {'a': 123, 'b': 'foo'}
#         self.assertDictEqual(f.query, {'$set': [{'a': 123, 'b': 'foo'}, {'b': 'foo'}]})
#
#     def test_field_query_4(self):
#         f = Field.make((int, str))
#         self.assertDictEqual(f.query, {})
#         f[1] = 'x'
#         self.assertDictEqual(f.query, {'$set': [None, 'x']})
#         f[0] = 123
#         self.assertDictEqual(f.query, {'$set': [123, 'x']})
#         f.set((123, 'x'))
#         self.assertDictEqual(f.query, {'$set': [123, 'x']})
#         f.set((456, 'foo'))
#         self.assertDictEqual(f.query, {'$set': [456, 'foo']})
#         del f[0]
#         self.assertDictEqual(f.query, {'$set': [None, 'foo']})
#         f.dirty_clear()
#         self.assertDictEqual(f.query, {})
#         f[0] = 123
#         self.assertDictEqual(f.query, {'$set': [123, 'foo']})
#
#     def test_field_query_5(self):
#         f = Field.make((int, {'a': int}))
#         self.assertDictEqual(f.query, {})
#         f['1.a'] = 123
#         self.assertDictEqual(f.query, {'$set': [None, {'a': 123}]})
#         f[0] = 123
#         self.assertDictEqual(f.query, {'$set': [123, {'a': 123}]})
#
#     def test_field_query_6(self):
#         data = {
#             'd1': int,
#             'd2': [str],
#             'd3': (int, str),
#             'd4': {
#                 'dd1': int,
#                 'dd2': [str],
#                 'dd3': (int, str)
#             },
#             'd5': {}
#         }
#         f = Field.make(data)
#         self.assertDictEqual(f.query, {})
#         f['d1'] = 123
#         self.assertDictEqual(f.query, {'$set': {'d1': 123}})
#         f['d2.0'] = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['123']
#         }})
#         f['d2'][1] = 'foo'
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['123', 'foo']
#         }})
#         f['d2'].append('bar')
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['123', 'foo', 'bar']
#         }})
#         f['d2'].set(['z', 123])
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123']
#         }})
#         f['d3.0'] = 123
#         f['d3.1'] = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [123, '123']
#         }})
#         f['d3'] = [None, 'foo']
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo']
#         }})
#         f['d4.dd1'] = 456
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456
#         }})
#         f['d4.dd2'].append('bar')
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456,
#             'd4.dd2': ['bar']
#         }})
#         f['d4.dd2.2'] = 'x'
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456,
#             'd4.dd2': ['bar', None, 'x']
#         }})
#         f['d4.dd3.1'] = 456
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456,
#             'd4.dd2': ['bar', None, 'x'],
#             'd4.dd3': [None, '456']
#         }})
#         f.dirty_clear()
#         self.assertDictEqual(f.query, {})
#         f.set({
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4.dd1': 123,
#             'd4.dd2': ['a', 'b', 'c'],
#             'd4.dd3': [None, None]
#         }})
#         f['d5'] = {'a': 1, 'b': 'foo'}
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4.dd1': 123,
#             'd4.dd2': ['a', 'b', 'c'],
#             'd4.dd3': [None, None],
#             'd5': {'a': 1, 'b': 'foo'}
#         }})
#         f['d4.dd3.1'] = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4.dd1': 123,
#             'd4.dd2': ['a', 'b', 'c'],
#             'd4.dd3': [None, '123'],
#             'd5': {'a': 1, 'b': 'foo'}
#         }})
#
#     def test_field_query_7(self):
#         f = Field.make({})
#         self.assertDictEqual(f.query, {})
#         f.set({
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         }})
