# coding: utf-8

import unittest
import datetime

from bson import ObjectId

from mokito.fields import (
    make_field,
    Field,
    IntField,
    FloatField,
    StringField,
    BooleanField,
    ObjectIdField,
    DateTimeField,
    ChoiceField
)
from mokito.errors import MokitoChoiceError


class TestFields(unittest.TestCase):

    def test_field(self):
        f = make_field()
        self.assertIsInstance(f, Field)
        self.assertIsNone(f.get())
        self.assertIsNone(f.value)
        self.assertIsNone(f.self_value)
        f.set(123)
        self.assertEqual(123, f.get())
        self.assertEqual(123, f.value)
        self.assertEqual(123, f.self_value)
        f.set('foo')
        self.assertEqual('foo', f.get())
        self.assertEqual('foo', f.value)
        self.assertEqual('foo', f.self_value)

    def test_int_field(self):
        f = make_field(int)
        self.assertIsInstance(f, IntField)
        self.assertIsNone(f.get())
        self.assertIsNone(f.value)
        self.assertIsNone(f.self_value)
        f.set(123)
        self.assertEqual(123, f.get())
        self.assertEqual(123, f.value)
        self.assertEqual(123, f.self_value)
        f.set('456')
        self.assertEqual(456, f.get())
        self.assertEqual(456, f.value)
        self.assertEqual(456, f.self_value)

    def test_float_field(self):
        f = make_field(float)
        self.assertIsInstance(f, FloatField)
        self.assertIsNone(f.get())
        self.assertIsNone(f.value)
        self.assertIsNone(f.self_value)
        f.set(123)
        self.assertEqual(123.0, f.get())
        self.assertEqual(123.0, f.value)
        self.assertEqual(123.0, f.self_value)
        f.set('456.7')
        self.assertEqual(456.7, f.get())
        self.assertEqual(456.7, f.value)
        self.assertEqual(456.7, f.self_value)

    def test_str_field(self):
        f = make_field(str)
        self.assertIsInstance(f, StringField)
        self.assertIsNone(f.get())
        self.assertIsNone(f.value)
        self.assertIsNone(f.self_value)
        f.set(123)
        self.assertEqual('123', f.get())
        self.assertEqual('123', f.value)
        self.assertEqual('123', f.self_value)
        f.set('456.7')
        self.assertEqual('456.7', f.get())
        self.assertEqual('456.7', f.value)
        self.assertEqual('456.7', f.self_value)

    def test_bool_field(self):
        f = make_field(bool)
        self.assertIsInstance(f, BooleanField)
        self.assertIsNone(f.get())
        self.assertIsNone(f.value)
        self.assertIsNone(f.self_value)
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
        f.set(False)
        self.assertFalse(f.get())
        self.assertFalse(f.value)
        self.assertFalse(f.self_value)

    def test_ObjectId_field(self):
        id1 = ObjectId()
        id2 = ObjectId()
        f = make_field(ObjectId)
        self.assertIsInstance(f, ObjectIdField)
        self.assertIsNone(f.get())
        self.assertIsNone(f.value)
        self.assertIsNone(f.self_value)
        self.assertIsNone(f.get(as_json=True))
        f.set(id1)
        self.assertEqual(id1, f.get())
        self.assertEqual(id1, f.value)
        self.assertEqual(id1, f.self_value)
        self.assertEqual(str(id1), f.get(as_json=True))
        f.set(str(id2))
        self.assertEqual(id2, f.get())
        self.assertEqual(id2, f.value)
        self.assertEqual(id2, f.self_value)
        self.assertEqual(str(id2), f.get(as_json=True))

    def test_datetime_field(self):
        dt1 = datetime.datetime.now()
        dt2 = datetime.datetime.utcnow()
        f = make_field(datetime.datetime)
        self.assertIsInstance(f, DateTimeField)
        self.assertIsNone(f.get())
        self.assertIsNone(f.value)
        self.assertIsNone(f.self_value)
        self.assertIsNone(f.get(as_json=True))
        f.set(dt1)
        self.assertEqual(dt1, f.get())
        self.assertEqual(dt1, f.value)
        self.assertEqual(dt1, f.self_value)
        self.assertEqual(dt1.replace(microsecond=0).isoformat(), f.get(date_format='iso'))
        self.assertEqual(dt1.strftime('%d/%m/%y'), f.get(date_format='%d/%m/%y'))
        f.set(dt2)
        self.assertEqual(dt2, f.get())
        self.assertEqual(dt2, f.value)
        self.assertEqual(dt2, f.self_value)
        self.assertEqual(dt2.replace(microsecond=0).isoformat(), f.get(date_format='iso'))
        self.assertEqual(dt2.strftime('%d/%m/%y'), f.get(date_format='%d/%m/%y'))
        f.set('14/12/16', date_format='%d/%m/%y')
        self.assertEqual(datetime.datetime(2016, 12, 14), f.value)
        self.assertEqual(datetime.datetime(2016, 12, 14), f.self_value)

    def test_choice_field(self):
        ch = {'a': 1, 'b': 2}
        x = ChoiceField(ch)
        f = make_field(x)
        self.assertDictEqual(x.choices, f.choices)

        f.set(1)
        self.assertEqual(f._val, 'a')
        self.assertEqual(f.get(), 1)

        f._val = 'c'
        self.assertIsNone(f.get())

        f.set(2)
        self.assertEqual(f._val, 'b')
        self.assertEqual(f.get(), 2)

        with self.assertRaises(MokitoChoiceError):
            f.set(333)

        self.assertEqual(f.get(), 2)
