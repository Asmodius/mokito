# import unittest
# import datetime
#
# from bson import ObjectId
#
# from mokito.fields import (
#     IntField,
#     FloatField,
#     StringField,
#     BooleanField,
#     ObjectIdField,
#     DateTimeField,
#     ChoiceField
# )
# from mokito.tools import make_field
# from mokito.errors import MokitoChoiceError
#
#
# class TestFields(unittest.TestCase):
#
#     def test_int_field(self):
#         f = make_field(int)
#         self.assertIsInstance(f, IntField)
#         self.assertFalse(f.dirty)
#         self.assertIsNone(f.value)
#         self.assertIsNone(f.self_value)
#         f.set_value(123)
#         self.assertEqual(123, f.value)
#         self.assertEqual(123, f.self_value)
#         f.value = 789
#         self.assertEqual(789, f.value)
#         self.assertEqual(789, f.self_value)
#
#         with self.assertRaises(ValueError):
#             f.set_value('aaa')
#         self.assertEqual(789, f.value)
#
#     def test_float_field(self):
#         f = make_field(float)
#         self.assertIsInstance(f, FloatField)
#         self.assertIsNone(f.value)
#         self.assertIsNone(f.self_value)
#         f.set_value(123)
#         self.assertEqual(123.0, f.value)
#         self.assertEqual(123.0, f.self_value)
#         f.value = '456.7'
#         self.assertEqual(456.7, f.value)
#         self.assertEqual(456.7, f.self_value)
#
#     def test_str_field(self):
#         f = make_field(str)
#         self.assertIsInstance(f, StringField)
#         self.assertIsNone(f.value)
#         self.assertIsNone(f.self_value)
#         f.set_value(123)
#         self.assertEqual('123', f.value)
#         self.assertEqual('123', f.self_value)
#         f.value = b'456.7'
#         self.assertEqual('456.7', f.value)
#         self.assertEqual('456.7', f.self_value)
#
#     def test_bool_field(self):
#         f = make_field(bool)
#         self.assertIsInstance(f, BooleanField)
#         self.assertIsNone(f.value)
#         self.assertIsNone(f.self_value)
#         f.set_value(123)
#         self.assertTrue(f.value)
#         self.assertTrue(f.self_value)
#         f.value = None
#         self.assertFalse(f.value)
#         self.assertFalse(f.self_value)
#
#     def test_ObjectId_field(self):
#         id1 = ObjectId()
#         id2 = ObjectId()
#         f = make_field(ObjectId)
#         self.assertIsInstance(f, ObjectIdField)
#         self.assertIsNone(f.value)
#         self.assertIsNone(f.self_value)
#         self.assertIsNone(f.get_value(_format='json'))
#         f.set_value(id1)
#         self.assertEqual(id1, f.value)
#         self.assertEqual(id1, f.self_value)
#         self.assertEqual(str(id1), f.get_value(_format='json'))
#         f.value = str(id2)
#         self.assertEqual(id2, f.value)
#         self.assertEqual(id2, f.self_value)
#         self.assertEqual(str(id2), f.get_value(_format='json'))
#
#     def test_datetime_field(self):
#         dt1 = datetime.datetime.now()
#         dt2 = datetime.datetime.utcnow()
#         f = make_field(datetime.datetime)
#         self.assertIsInstance(f, DateTimeField)
#         self.assertIsNone(f.value)
#         self.assertIsNone(f.self_value)
#         self.assertIsNone(f.get_value(as_json=True))
#         f.set_value(dt1)
#         self.assertEqual(dt1, f.value)
#         self.assertEqual(dt1, f.self_value)
#         self.assertEqual(dt1.replace(microsecond=0).isoformat(), f.get_value(_date_format='iso'))
#         self.assertEqual(dt1.strftime('%d/%m/%y'), f.get_value(_date_format='%d/%m/%y'))
#         f.value = dt2
#         self.assertEqual(dt2, f.value)
#         self.assertEqual(dt2, f.self_value)
#         self.assertEqual(dt2.replace(microsecond=0).isoformat(), f.get_value(_date_format='iso'))
#         self.assertEqual(dt2.strftime('%d/%m/%y'), f.get_value(_date_format='%d/%m/%y'))
#         f.set_value('14/12/16', _date_format='%d/%m/%y')
#         self.assertEqual(datetime.datetime(2016, 12, 14), f.value)
#         self.assertEqual(datetime.datetime(2016, 12, 14), f.self_value)
#
#     def test_choice_field(self):
#         f = make_field(ChoiceField({1: 'a', 2: 'b'}))
#
#         with self.assertRaises(MokitoChoiceError):
#             f.value = 1
#
#         f.set_value(1, inner=True)
#         self.assertEqual(f.value, 'a')
#         self.assertEqual(f.get_value(inner=True), 1)
#
#         f.value = 'b'
#         self.assertEqual(f.value, 'b')
#         self.assertEqual(f.get_value(inner=True), 2)
#
#         f._val = 111
#         self.assertIsNone(f.value)
