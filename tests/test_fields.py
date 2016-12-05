# # coding: utf-8
#
# import unittest
# import datetime
#
# from bson import ObjectId
# from bson.errors import InvalidId
#
# from mokito.model import (
#     Field,
#     IntField,
#     FloatField,
#     StringField,
#     BooleanField,
#     ObjectIdField,
#     DateTimeField
# )
#
#
# class TestFields(unittest.TestCase):
#
#     def test_field_1(self):
#         f = Field.make()
#         self.assertIsInstance(f, Field)
#         self.assertIsNone(f.get())
#         self.assertIsNone(f.value)
#         f.set(123)
#         self.assertEqual(123, f.get())
#         self.assertEqual(123, f.value)
#         f.set('foo')
#         self.assertEqual('foo', f.get())
#         self.assertEqual('foo', f.value)
#
#     def test_field_2(self):
#         f = Field.make()
#         f.setdefault(123)
#         f.setdefault(456)
#         self.assertEqual(123, f.get())
#         self.assertEqual(123, f.value)
#         f.set(None)
#         f.setdefault(456)
#         self.assertEqual(456, f.get())
#         self.assertEqual(456, f.value)
#
#     def test_int_field_1(self):
#         f = Field.make(int)
#         self.assertIsInstance(f, IntField)
#         self.assertIsNone(f.get())
#         self.assertIsNone(f.value)
#         f.set(123)
#         self.assertEqual(123, f.get())
#         self.assertEqual(123, f.value)
#         f.set('456')
#         self.assertEqual(456, f.get())
#         self.assertEqual(456, f.value)
#
#     def test_int_field_2(self):
#         f = Field.make(int)
#         f.setdefault('123')
#         f.setdefault(456)
#         self.assertEqual(123, f.get())
#         self.assertEqual(123, f.value)
#         f.set(None)
#         f.setdefault(456)
#         self.assertEqual(456, f.get())
#         self.assertEqual(456, f.value)
#
#     def test_float_field_1(self):
#         f = Field.make(float)
#         self.assertIsInstance(f, FloatField)
#         self.assertIsNone(f.get())
#         self.assertIsNone(f.value)
#         f.set(123)
#         self.assertEqual(123.0, f.get())
#         self.assertEqual(123.0, f.value)
#         f.set('456.7')
#         self.assertEqual(456.7, f.get())
#         self.assertEqual(456.7, f.value)
#
#     def test_float_field_2(self):
#         f = Field.make(float)
#         f.setdefault('123')
#         f.setdefault(456)
#         self.assertEqual(123.0, f.get())
#         self.assertEqual(123.0, f.value)
#         f.set(None)
#         f.setdefault(456.7)
#         self.assertEqual(456.7, f.get())
#         self.assertEqual(456.7, f.value)
#
#     def test_str_field_1(self):
#         f = Field.make(str)
#         self.assertIsInstance(f, StringField)
#         self.assertIsNone(f.get())
#         self.assertIsNone(f.value)
#         f.set(123)
#         self.assertEqual('123', f.get())
#         self.assertEqual('123', f.value)
#         f.set('456.7')
#         self.assertEqual('456.7', f.get())
#         self.assertEqual('456.7', f.value)
#
#     def test_str_field_2(self):
#         f = Field.make(str)
#         f.setdefault('foo')
#         f.setdefault(456)
#         self.assertEqual('foo', f.get())
#         self.assertEqual('foo', f.value)
#         f.set(None)
#         f.setdefault(456.7)
#         self.assertEqual('456.7', f.get())
#         self.assertEqual('456.7', f.value)
#
#     def test_bool_field_1(self):
#         f = Field.make(bool)
#         self.assertIsInstance(f, BooleanField)
#         self.assertIsNone(f.get())
#         self.assertIsNone(f.value)
#         f.set(123)
#         self.assertTrue(f.get())
#         self.assertTrue(f.value)
#         f.set(True)
#         self.assertTrue(f.get())
#         self.assertTrue(f.value)
#         f.set(False)
#         self.assertFalse(f.get())
#         self.assertFalse(f.value)
#
#     def test_bool_field_2(self):
#         f = Field.make(bool)
#         f.setdefault(True)
#         f.setdefault(False)
#         self.assertTrue(f.get())
#         self.assertTrue(f.value)
#         f.set(None)
#         f.setdefault(False)
#         self.assertFalse(f.get())
#         self.assertFalse(f.value)
#
#     def test_ObjectId_field_1(self):
#         id1 = ObjectId()
#         id2 = ObjectId()
#         f = Field.make(ObjectId)
#         self.assertIsInstance(f, ObjectIdField)
#         self.assertIsNone(f.get())
#         self.assertIsNone(f.value)
#         f.set(id1)
#         self.assertEqual(id1, f.get())
#         self.assertEqual(id1, f.value)
#         f.set(str(id2))
#         self.assertEqual(id2, f.get())
#         self.assertEqual(id2, f.value)
#
#     def test_ObjectId_field_2(self):
#         id1 = ObjectId()
#         id2 = ObjectId()
#         f = Field.make(ObjectId)
#         f.setdefault(id1)
#         f.setdefault(id2)
#         self.assertEqual(id1, f.get())
#         self.assertEqual(id1, f.value)
#         f.set(None)
#         f.setdefault(id2)
#         self.assertEqual(id2, f.get())
#         self.assertEqual(id2, f.value)
#
#     def test_datetime_field_1(self):
#         dt1 = datetime.datetime.now()
#         dt2 = datetime.datetime.utcnow()
#         f = Field.make(datetime.datetime)
#         self.assertIsInstance(f, DateTimeField)
#         self.assertIsNone(f.get())
#         self.assertIsNone(f.value)
#         f.set(dt1)
#         self.assertEqual(dt1, f.get())
#         self.assertEqual(dt1, f.value)
#         f.set(dt2)
#         self.assertEqual(dt2, f.get())
#         self.assertEqual(dt2, f.value)
#
#     def test_datetime_field_2(self):
#         dt1 = datetime.datetime.now()
#         dt2 = datetime.datetime.utcnow()
#         f = Field.make(datetime.datetime)
#         f.setdefault(dt1)
#         f.setdefault(dt2)
#         self.assertEqual(dt1, f.get())
#         self.assertEqual(dt1, f.value)
#         f.set(None)
#         f.setdefault(dt2)
#         self.assertEqual(dt2, f.get())
#         self.assertEqual(dt2, f.value)
