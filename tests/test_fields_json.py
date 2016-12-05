# # coding: utf-8
#
# import unittest
# import datetime
#
# from bson import ObjectId
#
# from mokito.model import Field
#
#
# class TestJson(unittest.TestCase):
#
#     def test_to_json_1(self):
#         import pytz
#
#         f = Field.make()
#         self.assertEqual(None, f.to_json())
#
#         f = Field.make(int)
#         self.assertEqual(None, f.to_json())
#         f.set(123)
#         self.assertEqual(123, f.to_json())
#
#         f = Field.make(str)
#         f.set('foo')
#         self.assertEqual('foo', f.to_json())
#
#         f = Field.make(float)
#         f.set(.5)
#         self.assertEqual(.5, f.to_json())
#
#         f = Field.make(ObjectId)
#         _id = ObjectId()
#         f.set(_id)
#         self.assertEqual(str(_id), f.to_json())
#
#         f = Field.make(bool)
#         f.set(True)
#         self.assertEqual(True, f.to_json())
#         f.set(False)
#         self.assertEqual(False, f.to_json())
#
#         f = Field.make(datetime.datetime)
#         dt = datetime.datetime.now()
#         f.set(dt)
#         self.assertEqual(dt.strftime('%Y-%m-%dT%H:%M:%S'), f.to_json())
#
#         dt = datetime.datetime.utcnow()
#         f.set(dt)
#         self.assertEqual(dt.strftime('%Y-%m-%dT%H:%M:%S'), f.to_json())
#         self.assertEqual((dt + datetime.timedelta(hours=7)).strftime('%Y-%m-%dT%H:%M:%S+07:00'),
#                          f.to_json(tz_name='Asia/Novosibirsk'))
#         tz = pytz.timezone('Asia/Novosibirsk')
#         self.assertEqual((dt + datetime.timedelta(hours=7)).strftime('%Y-%m-%dT%H:%M:%S+07:00'),
#                          f.to_json(tz=tz))
#
#         f = Field.make([str])
#         self.assertEqual([], f.to_json())
#         f.set(['foo', 'bar'])
#         self.assertEqual(["foo", "bar"], f.to_json())
#         f[3] = 'x'
#         self.assertEqual(["foo", "bar", None, "x"], f.to_json())
#         f.set(['foo', 'bar'])
#         self.assertEqual(["foo", "bar"], f.to_json())
#         f[3] = 'x'
#         self.assertEqual(["foo", "bar", None, "x"], f.to_json())
#
#         f = Field.make([datetime.datetime])
#         self.assertEqual([], f.to_json())
#         dt1 = datetime.datetime(2016, 2, 3, 4, 5, 6, 7)
#         dt2 = datetime.datetime(2016, 3, 4, 5, 6, 7, 8)
#         f.set([dt1, dt2])
#         self.assertEqual(["2016-02-03T04:05:06", "2016-03-04T05:06:07"], f.to_json())
#         self.assertEqual(["2016-02-03T10:05:06+06:00", "2016-03-04T11:06:07+06:00"],
#                          f.to_json(tz_name='Asia/Novosibirsk'))
#         self.assertEqual(["2016-02-03T04:05:06", "2016-03-04T11:06:07+06:00"],
#                          f.to_json(**{'1.tz_name': 'Asia/Novosibirsk'}))
#
#         f = Field.make((str, int))
#         f.set(['foo', 123])
#         self.assertEqual(["foo", 123], f.to_json())
#
#         dt1 = datetime.datetime(2016, 2, 3, 4, 5, 6, 7)
#         dt2 = datetime.datetime(2016, 3, 4, 5, 6, 7, 8)
#         dt3 = datetime.datetime(2016, 4, 5, 6, 7, 8, 9)
#         dt4 = datetime.datetime(2016, 5, 6, 7, 8, 9, 10)
#
#         f = Field.make({
#             'f1': int,
#             'f2': str,
#             'f3': [datetime.datetime],
#             'f4': (str, datetime.datetime),
#             'f5': {}
#         })
#         self.assertDictEqual(f.to_json(), {
#             'f1': None,
#             'f2': None,
#             'f3': [],
#             'f4': [None, None],
#             'f5': {}
#         })
#         f['f1'] = 123
#         f['f2'] = 'foo'
#         f['f3'].set([dt1, dt2])
#         f['f4'].set(['bar', dt3])
#         f['f5'].set({'a': dt4, 'b': True})
#         self.assertDictEqual(f.to_json(), {
#             'f1': 123,
#             'f2': 'foo',
#             'f3': ['2016-02-03T04:05:06', '2016-03-04T05:06:07'],
#             'f4': ['bar', '2016-04-05T06:07:08'],
#             'f5': {'a': '2016-05-06T07:08:09', 'b': True}
#         })
#         self.assertDictEqual(f.to_json(tz_name='Asia/Novosibirsk'), {
#             'f1': 123,
#             'f2': 'foo',
#             'f3': ['2016-02-03T10:05:06+06:00', '2016-03-04T11:06:07+06:00'],
#             'f4': ['bar', '2016-04-05T12:07:08+06:00'],
#             'f5': {'a': '2016-05-06T13:08:09+06:00', 'b': True}
#         })
#         param = {
#             'f3.1.tz_name': 'Asia/Novosibirsk',
#             'f4._format': '%d/%m/%y',
#             'f5.tz_name': 'Europe/Moscow'
#         }
#         self.assertDictEqual(f.to_json(**param), {
#             'f1': 123,
#             'f2': 'foo',
#             'f3': ['2016-02-03T04:05:06', '2016-03-04T11:06:07+06:00'],
#             'f4': ['bar', '05/04/16'],
#             'f5': {'a': '2016-05-06T10:08:09+03:00', 'b': True}
#         })
#
#     def test_to_json_2(self):
#         f = Field.make([str])
#         f.set(['foo', 'bar'])
#         self.assertEqual(["bar"], f.to_json(1))
#         f[3] = 'x'
#         self.assertEqual(["foo", "x"], f.to_json(0, 3))
#         f.set(['foo', 'bar'])
#         self.assertEqual(["foo", None], f.to_json(0, 3))
#         self.assertEqual(["foo", None], f.to_json(0, 3, 0))
#         f[3] = 'x'
#         self.assertEqual(["foo", "x", "bar"], f.to_json(0, 3, 1))
#
#         f = Field.make([datetime.datetime])
#         self.assertEqual([], f.to_json())
#         dt1 = datetime.datetime(2016, 2, 3, 4, 5, 6, 7)
#         dt2 = datetime.datetime(2016, 3, 4, 5, 6, 7, 8)
#         f.set([dt1, dt2])
#         self.assertEqual(["2016-02-03T04:05:06"], f.to_json(0))
#         self.assertEqual(["2016-03-04T11:06:07+06:00"], f.to_json(1, tz_name='Asia/Novosibirsk'))
#
#         f = Field.make((str, int))
#         f.set(['foo', 123])
#         self.assertEqual([123, "foo"], f.to_json(1, 0))
#
#         dt1 = datetime.datetime(2016, 2, 3, 4, 5, 6, 7)
#         dt2 = datetime.datetime(2016, 3, 4, 5, 6, 7, 8)
#         dt3 = datetime.datetime(2016, 4, 5, 6, 7, 8, 9)
#         dt4 = datetime.datetime(2016, 5, 6, 7, 8, 9, 10)
#
#         f = Field.make({
#             'f1': int,
#             'f2': str,
#             'f3': [datetime.datetime],
#             'f4': (str, datetime.datetime),
#             'f5': {}
#         })
#         f['f1'] = 123
#         f['f2'] = 'foo'
#         f['f3'].set([dt1, dt2])
#         f['f4'].set(['bar', dt3])
#         f['f5'].set({'a': dt4, 'b': True})
#         self.assertDictEqual(f.to_json('f1', 'f3.1', 'f5.b'), {
#             'f1': 123,
#             'f3': ['2016-03-04T05:06:07'],
#             'f5': {'b': True}
#         })
#         self.assertDictEqual(f.to_json('f3', 'f4.1', 'f5.a', tz_name='Asia/Novosibirsk'), {
#             'f3': ['2016-02-03T10:05:06+06:00', '2016-03-04T11:06:07+06:00'],
#             'f4': ['2016-04-05T12:07:08+06:00'],
#             'f5': {'a': '2016-05-06T13:08:09+06:00'}
#         })
#         param = {
#             'f3.1.tz_name': 'Asia/Novosibirsk',
#             'f4._format': '%d/%m/%y',
#             'f5.tz_name': 'Europe/Moscow'
#         }
#         self.assertDictEqual(f.to_json('f2', 'f3', 'f4', 'f5', **param), {
#             'f2': 'foo',
#             'f3': ['2016-02-03T04:05:06', '2016-03-04T11:06:07+06:00'],
#             'f4': ['bar', '05/04/16'],
#             'f5': {'a': '2016-05-06T10:08:09+03:00', 'b': True}
#         })
#
#     def test_from_json_1(self):
#         f = Field.make(int)
#         f.from_json('456')
#         self.assertEqual(f.value, 456)
#         f.from_json('null')
#         self.assertEqual(f.value, None)
#
#         f = Field.make(str)
#         f.from_json('"foo"')
#         self.assertEqual(f.value, 'foo')
#         f.from_json('null')
#         self.assertEqual(f.value, None)
#
#         f = Field.make(float)
#         f.from_json('0.5')
#         self.assertEqual(f.value, .5)
#         f.from_json('null')
#         self.assertEqual(f.value, None)
#
#         f = Field.make(ObjectId)
#         _id = ObjectId()
#         f.from_json('"%s"' % _id)
#         self.assertEqual(f.value, _id)
#         f.from_json('null')
#         self.assertEqual(f.value, None)
#
#         f = Field.make(bool)
#         f.from_json('true')
#         self.assertEqual(f.value, True)
#         f.from_json('false')
#         self.assertEqual(f.value, False)
#         f.from_json('null')
#         self.assertEqual(f.value, None)
#
#         f = Field.make(datetime.datetime)
#         f.from_json('"2016-01-27T05:57:31.399861Z"')
#         self.assertEqual(f.value, datetime.datetime(2016, 1, 27, 5, 57, 31, 399861))
#         f.from_json('"2016-02-27T05:57:31.399861"')
#         self.assertEqual(f.value, datetime.datetime(2016, 2, 27, 5, 57, 31, 399861))
#         f.from_json('"2016-03-27T05:57:31"')
#         self.assertEqual(f.value, datetime.datetime(2016, 3, 27, 5, 57, 31))
#         f.from_json('"27/03/16"', _format='%d/%m/%y')
#         self.assertEqual(f.value, datetime.datetime(2016, 3, 27))
#
#         f = Field.make([str])
#         f.from_json('["foo", null, "bar"]')
#         self.assertEqual(f.value, ['foo', None, 'bar'])
#         f.from_json('null')
#         self.assertEqual(f.value, [])
#
#         f = Field.make([datetime.datetime])
#         param = {'1._format': '%d/%m/%y'}
#         f.from_json('["2016-01-27T05:57:31.399861Z", "27/03/16"]', **param)
#         self.assertEqual(f.value, [datetime.datetime(2016, 1, 27, 5, 57, 31, 399861),
#                                    datetime.datetime(2016, 3, 27)])
#
#         f = Field.make((str, datetime.datetime))
#         param = {'_format': '%d/%m/%y'}
#         f.from_json('["27/03/16", "27/03/16"]', **param)
#         self.assertEqual(f.value, ['27/03/16', datetime.datetime(2016, 3, 27)])
#
#         f = Field.make({
#             'f1': int,
#             'f2': str,
#             'f3': [datetime.datetime],
#             'f4': (str, datetime.datetime),
#             'f5': {}
#         })
#         f.from_json('''{
#             "f1": 123,
#             "f2": "foo",
#             "f3": ["2016-02-03T04:05:06", "2016-03-04T05:06:07"],
#             "f4": ["bar", "2016-04-05T06:07:08"],
#             "f5": {"a": "2016-05-06T07:08:09", "b": true}
#         }''')
#         self.assertDictEqual(f.value, {
#             'f1': 123,
#             'f2': 'foo',
#             'f3': [datetime.datetime(2016, 2, 3, 4, 5, 6), datetime.datetime(2016, 3, 4, 5, 6, 7)],
#             'f4': ['bar', datetime.datetime(2016, 4, 5, 6, 7, 8)],
#             'f5': {'a': '2016-05-06T07:08:09', 'b': True}
#         })
#         param = {'f4.1._format': '%d/%m/%y'}
#         f.from_json('''{
#             "f1": 123,
#             "f2": "foo",
#             "f3": ["2016-03-03T04:05:06", "2016-04-04T05:06:07"],
#             "f4": ["bar", "27/03/16"]
#         }''', **param)
#         self.assertDictEqual(f.value, {
#             'f1': 123,
#             'f2': 'foo',
#             'f3': [datetime.datetime(2016, 3, 3, 4, 5, 6), datetime.datetime(2016, 4, 4, 5, 6, 7)],
#             'f4': ['bar', datetime.datetime(2016, 3, 27, 0, 0)],
#             'f5': {}
#         })
#
#     # def test_from_json_2(self):
#     #     # DOT
