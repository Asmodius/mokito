# coding: utf-8

import unittest
import datetime

from bson import ObjectId

from mokito.fields import (
    make_field,
    IntField,
    FloatField,
    StringField,
    BooleanField,
    ObjectIdField,
    DateTimeField
)


class TestFieldsDefault(unittest.TestCase):

    def test_int_field_default(self):
        f = make_field(123)
        self.assertTrue(f.dirty)
        self.assertIsInstance(f, IntField)
        self.assertEqual(123, f.get())
        self.assertEqual(123, f.value)
        self.assertEqual(123, f.self_value)
        f.set('456')
        self.assertEqual(456, f.get())
        self.assertEqual(456, f.value)
        self.assertEqual(456, f.self_value)
        f.value = 789
        self.assertEqual(789, f.get())
        self.assertEqual(789, f.value)
        self.assertEqual(789, f.self_value)

        with self.assertRaises(ValueError):
            f.set('aaa')
        self.assertEqual(789, f.value)

    def test_float_field_const(self):
        f = make_field(123.4)
        self.assertIsInstance(f, FloatField)
        self.assertEqual(123.4, f.get())
        self.assertEqual(123.4, f.value)
        self.assertEqual(123.4, f.self_value)
        f.set(789)
        self.assertEqual(789.0, f.get())
        self.assertEqual(789.0, f.value)
        self.assertEqual(789.0, f.self_value)
        f.set('456.7')
        self.assertEqual(456.7, f.get())
        self.assertEqual(456.7, f.value)
        self.assertEqual(456.7, f.self_value)

    def test_str_field_const(self):
        f = make_field('foo')
        self.assertIsInstance(f, StringField)
        self.assertEqual('foo', f.get())
        self.assertEqual('foo', f.value)
        self.assertEqual('foo', f.self_value)
        f.set(456.7)
        self.assertEqual('456.7', f.get())
        self.assertEqual('456.7', f.value)
        self.assertEqual('456.7', f.self_value)

    def test_bool_field_const(self):
        f = make_field(True)
        self.assertIsInstance(f, BooleanField)
        self.assertTrue(f.get())
        self.assertTrue(f.value)
        self.assertTrue(f.self_value)
        f.set(123)
        self.assertTrue(f.get())
        self.assertTrue(f.value)
        self.assertTrue(f.self_value)
        f.set(None)
        self.assertFalse(f.get())
        self.assertFalse(f.value)
        self.assertFalse(f.self_value)
        f.set(True)
        self.assertTrue(f.get())
        self.assertTrue(f.value)
        self.assertTrue(f.self_value)
        f.value = False
        self.assertFalse(f.get())
        self.assertFalse(f.value)
        self.assertFalse(f.self_value)

    def test_ObjectId_field_const(self):
        id1 = ObjectId()
        id2 = ObjectId()
        f = make_field(id1)
        self.assertIsInstance(f, ObjectIdField)
        self.assertEqual(id1, f.get())
        self.assertEqual(id1, f.value)
        self.assertEqual(id1, f.self_value)
        self.assertEqual(str(id1), f.get(_format='json'))
        f.set(str(id2))
        self.assertEqual(id2, f.get())
        self.assertEqual(id2, f.value)
        self.assertEqual(id2, f.self_value)
        self.assertEqual(str(id2), f.get(_format='json'))
        f.value = str(id1)
        self.assertEqual(id1, f.get())
        self.assertEqual(id1, f.value)
        self.assertEqual(id1, f.self_value)
        self.assertEqual(str(id1), f.get(_format='json'))

    def test_datetime_field_const(self):
        dt1 = datetime.datetime.now()
        dt2 = datetime.datetime.utcnow()
        f = make_field(dt1)
        self.assertIsInstance(f, DateTimeField)
        self.assertEqual(dt1, f.get())
        self.assertEqual(dt1, f.value)
        self.assertEqual(dt1, f.self_value)
        self.assertEqual(dt1.replace(microsecond=0).isoformat(), f.get(_date_format='iso'))
        self.assertEqual(dt1.strftime('%d/%m/%y'), f.get(_date_format='%d/%m/%y'))
        f.set(dt2)
        self.assertEqual(dt2, f.get())
        self.assertEqual(dt2, f.value)
        self.assertEqual(dt2, f.self_value)
        self.assertEqual(dt2.replace(microsecond=0).isoformat(), f.get(_date_format='iso'))
        self.assertEqual(dt2.strftime('%d/%m/%y'), f.get(_date_format='%d/%m/%y'))
