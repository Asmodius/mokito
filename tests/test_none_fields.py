# import unittest
#
# from mokito.fields import AnyField
# from mokito.tools import make_field
# from mokito.collections import ListField, TupleField
#
#
# class TestNoneFields(unittest.TestCase):
#     def test_list_field_1(self):
#         f = make_field([None])
#         self.assertIsInstance(f, ListField)
#         self.assertIsInstance(f._rules, AnyField)
#         f[1].value = 123
#         f.append_value('foo')
#         self.assertIsNone(f.pop(0).value)
#         self.assertListEqual(f.value, [123, 'foo'])
#         f[1].value = None
#         self.assertListEqual(f.value, [123, None])
#         del f[1]
#         self.assertListEqual(f.value, [123])
#
#         f.append_value(('bar', 2))
#         self.assertListEqual(f.value, [123, ['bar', 2]])
#         self.assertEqual(f[1][1].value, 2)
#         self.assertEqual(f['1.1'].value, 2)
#
#     def test_tuple_field_1(self):
#         f = make_field((None, str))
#         self.assertIsInstance(f, TupleField)
#         self.assertListEqual(f.value, [None, None])
#         f[0].value = 123
#         f[1].value = 123
#         self.assertListEqual(f.value, [123, '123'])
#         f[0].value = 'foo'
#         self.assertListEqual(f.value, ['foo', '123'])
#         del f[0]
#         self.assertListEqual(f.value, [None, '123'])
#
#     def test_tuple_field_2(self):
#         f = make_field((str, [None]))
#         self.assertListEqual(f.value, [None, []])
#         f.set_value(['foo', [1, 'bar']])
#         self.assertListEqual(f.value, ['foo', [1, 'bar']])
#         f[1].append_value(123.4)
#         self.assertListEqual(f.value, ['foo', [1, 'bar', 123.4]])
#         del f['1.1']
#         self.assertListEqual(f.value, ['foo', [1, 123.4]])
#         f[1].value = None
#         self.assertListEqual(f.value, ['foo', []])
#
#     def test_dict_field_1(self):
#         f = make_field({
#             'a': int,
#             'b': None
#         })
#         self.assertDictEqual(f.value, {'a': None, 'b': None})
#
#         f.set_value({'a': 123, 'b': 456})
#         self.assertDictEqual(f.value, {'a': 123, 'b': 456})
#
#         f.set_value({'a': 1, 'b': [1, 2, 3]})
#         self.assertDictEqual(f.value, {'a': 1, 'b': [1, 2, 3]})
#
#         f.clear()
#         self.assertDictEqual(f.value, {'a': None, 'b': None})
#
#     def test_list_query_1(self):
#         f = make_field([None])
#         self.assertDictEqual(f.query, {})
#         f.append_value('foo')
#         self.assertDictEqual(f.query, {'$set': ['foo']})
#         f.append_value(123)
#         self.assertDictEqual(f.query, {'$set': ['foo', 123]})
#         del f[0]
#         self.assertDictEqual(f.query, {'$set': [123]})
#         f.dirty_clear()
#         self.assertDictEqual(f.query, {})
#         f[1].value = ('x', 456.7)
#         self.assertDictEqual(f.query, {'$set': [123, ['x', 456.7]]})
#         f.pop(0)
#         self.assertDictEqual(f.query, {'$set': [['x', 456.7]]})
#         f.dirty_clear()
#         del f[0]
#         self.assertDictEqual(f.query, {'$set': []})
#
#     def test_tuple_query_1(self):
#         f = make_field((int, None))
#         self.assertDictEqual(f.query, {})
#         f[0].value = 123
#         self.assertDictEqual(f.query, {'$set': [123, None]})
#         f[1].value = 'foo'
#         self.assertDictEqual(f.query, {'$set': [123, 'foo']})
#         f.dirty_clear()
#         self.assertDictEqual(f.query, {})
#         del f[0]
#         self.assertDictEqual(f.query, {'$set': [None, 'foo']})
#
#     def test_list_tuple_query_1(self):
#         f = make_field((str, [None]))
#         self.assertDictEqual(f.query, {})
#         f.set_value(['foo', [1]])
#         self.assertDictEqual(f.query, {'$set': ['foo', [1]]})
#         f['1.2'].value = 'bar'
#         self.assertDictEqual(f.query, {'$set': ['foo', [1, None, 'bar']]})
#
#     def test_list_query_2(self):
#         f = make_field([{'a': int, 'b': None}])
#         self.assertDictEqual(f.query, {})
#         f.append_value({'a': 1})
#         self.assertDictEqual(f.query, {'$set': [{'a': 1, 'b': None}]})
#         f.append_value({'b': 'foo'})
#         self.assertDictEqual(f.query, {'$set': [{'a': 1, 'b': None}, {'a': None, 'b': 'foo'}]})
#         f[0].value = {'a': 123, 'b': 456.7}
#         self.assertDictEqual(f.query, {'$set': [{'a': 123, 'b': 456.7}, {'a': None, 'b': 'foo'}]})
