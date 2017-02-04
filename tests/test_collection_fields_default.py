# coding: utf-8

import unittest

from mokito.fields import (
    make_field,
    IntField,
    FloatField,
    StringField,
    DictField,
    TupleField,
    ListField
)


class TestCollectionFieldsDefault(unittest.TestCase):
    def test_list_field_1(self):
        f = make_field([123])
        self.assertIsInstance(f, ListField)
        self.assertIsInstance(f._rules, IntField)
        self.assertListEqual(f.value, [123])

        f.append('111')
        self.assertListEqual(f.value, [123, 111])

        f.set(None)
        self.assertListEqual(f.value, [])

    def test_tuple_field_1(self):
        f = make_field((123, 'foo'))
        self.assertIsInstance(f, TupleField)
        self.assertIsInstance(f._val['0'], IntField)
        self.assertTrue(f == f._val['0']._parent)
        self.assertIsInstance(f._val['1'], StringField)
        self.assertTrue(f == f._val['1']._parent)
        self.assertListEqual(f.value, [123, 'foo'])

        f[0] = 456
        self.assertEqual(f.value, [456, 'foo'])
        self.assertEqual(f.self_value, [456, 'foo'])
        self.assertEqual(f.get(), [456, 'foo'])
        self.assertTrue(f == f[0]._parent)

        f[1] = 456
        self.assertEqual(f.value, [456, '456'])
        self.assertEqual(f.self_value, [456, '456'])
        self.assertEqual(f.get(), [456, '456'])
        self.assertTrue(f == f[1]._parent)

        f[0] = None
        self.assertEqual(f.value, [None, '456'])
        self.assertEqual(f.self_value, [None, '456'])
        self.assertEqual(f.get(), [None, '456'])
        self.assertTrue(f == f[0]._parent)

        del f[1]
        self.assertEqual(f.value, [None, None])
        self.assertEqual(f.self_value, [None, None])
        self.assertEqual(f.get(), [None, None])
        self.assertTrue(f == f[1]._parent)

    def test_dict_field_1(self):
        data = {
            'f0': 'foo',
            'f1': 123,
            'f2': 456.7,
        }
        f = make_field(data)
        self.assertIsInstance(f, DictField)
        self.assertIsInstance(f._val['f0'], StringField)
        self.assertTrue(f == f._val['f0']._parent)
        self.assertIsInstance(f._val['f1'], IntField)
        self.assertTrue(f == f._val['f1']._parent)
        self.assertIsInstance(f._val['f2'], FloatField)
        self.assertTrue(f == f._val['f2']._parent)

        self.assertDictEqual(f.value, {'f0': 'foo', 'f1': 123, 'f2': 456.7})
        f.set({'f0': 'bar', 'f1': 456})
        self.assertDictEqual(f.value, {'f0': 'bar', 'f1': 456, 'f2': 456.7})
        f['f2'] = 9
        self.assertDictEqual(f.value, {'f0': 'bar', 'f1': 456, 'f2': 9.0})

    def test_list_query_1(self):
        f = make_field(['foo'])
        self.assertDictEqual(f.query, {'$set': ['foo']})
        f.append('bar')
        self.assertDictEqual(f.query, {'$set': ['foo', 'bar']})
        del f[0]
        self.assertDictEqual(f.query, {'$set': ['bar']})
        f.dirty_clear()
        self.assertDictEqual(f.query, {})
        f[1] = 'x'
        self.assertDictEqual(f.query, {'$set': ['bar', 'x']})

    def test_tuple_query_1(self):
        f = make_field((123, str))
        self.assertDictEqual(f.query, {'$set': [123, None]})
        f[1] = 'foo'
        self.assertDictEqual(f.query, {'$set': [123, 'foo']})
        f.dirty_clear()
        self.assertDictEqual(f.query, {})
        del f[0]
        self.assertDictEqual(f.query, {'$set': [None, 'foo']})
