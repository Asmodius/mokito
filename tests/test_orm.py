# coding: utf-8

import datetime

from bson import ObjectId, DBRef
from bson.errors import InvalidId
from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, gen_test

import mokito

from tests.util import (
    TEST_DB_NAME,
    TEST_COLLECTION1,
    TEST_COLLECTION2,
    col1_id1,
    col1_data1,
    col1_id2,
    col1_data2,
    col2_id1,
    col2_data1,
    col2_id2,
    col2_data2,
    Document1,
    Document2
)


class ORMTestCase(AsyncTestCase):
    def get_new_ioloop(self):
        return IOLoop.instance()

    @gen_test
    def _init_collection(self):
        yield self.db[TEST_COLLECTION1].insert([col1_data1, col1_data2])
        yield self.db[TEST_COLLECTION2].insert([col2_data1, col2_data2])

    def setUp(self):
        super(ORMTestCase, self).setUp()
        self.db = mokito.DBManager[TEST_DB_NAME]
        self._init_collection()

    @gen_test
    def tearDown(self):
        yield self.db.command('drop', TEST_COLLECTION2)
        yield self.db.command('drop', TEST_COLLECTION1)
        super(ORMTestCase, self).tearDown()

    def test_databases(self):
        self.assertIsInstance(mokito.DBManager[TEST_DB_NAME], mokito.Client)

    # @gen_test
    # def test_find_one_1(self):
    #     x = yield Document1.find_one(col1_id1)
    #     self.assertEqual(x._id, col1_id1)
    #     y = yield Document1.by_id(col1_id1)
    #     self.assertEqual(y._id, col1_id1)
    #
    #     data = col1_data1.copy()
    #     data.pop('_id')
    #     self.assertDictEqual(data, x._data.value)
    #     self.assertDictEqual(data, y._data.value)
    #
    #     x = yield Document1.find_one(col1_id2)
    #     y = yield Document1.by_id(col1_id2)
    #     self.assertEqual(x._id, col1_id2)
    #     self.assertEqual(y._id, col1_id2)
    #     data = col1_data2.copy()
    #     data.pop('_id')
    #     data.pop('foo')
    #     self.assertDictEqual(data, x._data.value)
    #     self.assertDictEqual(data, y._data.value)
    #
    # @gen_test
    # def test_find_one_2(self):
    #     _id = ObjectId()
    #     x = yield Document1.find_one(_id)
    #     self.assertIsNone(x)
    #
    #     with self.assertRaises(InvalidId):
    #         yield Document1.find_one('foo')
    #
    #     with self.assertRaises(mokito.errors.MokitoORMError):
    #         yield Document1.by_id(_id)
    #
    # @gen_test
    # def test_find_1(self):
    #     x = yield Document1.find()
    #     self.assertEqual(len(x), 2)
    #
    #     data = col1_data1.copy()
    #     data.pop('_id')
    #     self.assertDictEqual(data, x[0]._data.value)
    #
    #     data = col1_data2.copy()
    #     data.pop('_id')
    #     data.pop('foo')
    #     self.assertDictEqual(data, x[1]._data.value)
    #
    # @gen_test
    # def test_count(self):
    #     self.assertEqual((yield Document1.count()), 2)
    #
    # @gen_test
    # def test_save_1(self):
    #     x = yield Document1.find_one(col1_id2)
    #     self.assertFalse(x.dirty)
    #     x['x1'] = 3
    #     self.assertTrue(x.dirty)
    #     self.assertDictEqual(x._data.query, {'$set': {'x1': 3.0}})
    #     y = yield x.save()
    #     self.assertTrue(y)
    #     self.assertFalse(x.dirty)
    #
    #     data = yield self.db[TEST_COLLECTION1].find_one(col1_id2, ['x1'])
    #     self.assertEqual(data['x1'], 3.0)
    #     self.assertEqual(x['x1'].value, 3.0)
    #
    #     data = yield self.db[TEST_COLLECTION1].count()
    #     self.assertEqual(data, 2)
    #
    # @gen_test
    # def test_save_2(self):
    #     data = col1_data1.copy()
    #     del data['_id']
    #
    #     x = Document1(**data)
    #     self.assertIsNone(x.id)
    #     self.assertTrue(x.dirty)
    #     self.assertDictEqual(x.value, data)
    #
    #     y = yield x.save()
    #     self.assertTrue(y)
    #     self.assertIsNotNone(x.id)
    #     self.assertFalse(x.dirty)
    #
    #     data = yield self.db[TEST_COLLECTION1].find_one(x._id)
    #     del data['_id']
    #     self.assertDictEqual(x.value, data)
    #     self.assertEqual((yield self.db[TEST_COLLECTION1].count()), 3)
    #
    # @gen_test
    # def test_to_prop(self):
    #     x = yield Document1.find_one(col1_id1)
    #     self.assertEqual(x.prop1, x['x1'].value + 2)
    #     self.assertEqual(x.prop2, x['x1'].value * 2)
    #     x['x1'] = 10
    #     self.assertEqual(x.prop1, 12.0)
    #     self.assertEqual(x.prop2, 20.0)

    # @gen_test
    # def test_to_json_1(self):
    #     x = yield Document1.find_one(col1_id1)
    #
    #     data = yield x.to_json('_id', 'x1', 'x2', 'x3', 'x4') ----
    #     self.assertDictEqual(data, {
    #         '_id': str(col1_id1),
    #         'x1': 0.5,
    #         'x2': ["2016-01-02T03:04:05", "2016-02-03T04:05:06", "2016-03-04T05:06:07"],
    #         'x3': [123, "foo"],
    #         'x4': {"a": 1, "b": 2}
    #     })
    #
    #     data = yield x.to_json('r2', tz_name='Asia/Novosibirsk')
    #     self.assertDictEqual(data, {
    #         'x2': ['2016-01-02T09:04:05+06:00', '2016-02-03T10:05:06+06:00', '2016-03-04T11:06:07+06:00'],
    #         'x3': [123, "foo"],
    #         'x4': {"a": 1, "b": 2}
    #     })
    #
    #     data = yield x.to_json('r3', 'r4')
    #     self.assertDictEqual(data, {
    #         'a1': 0.5,
    #         'a2': 2.5,
    #         'a3': 1.0,
    #         'prop1': 2.5,
    #         'prop2': 1.0
    #     })
    #
    #     data = yield x.to_json('r5')
    #     print data
    #     self.assertDictEqual(data, {
    #         'x3.1': 'foo',
    #         'x4.a': 1,
    #         'x4.b': 2
    #     })
    #
    # @gen_test
    # def test_to_json_2(self):
    #     x = yield Document1.find()
    #
    #     # data = yield x.to_json('r1', 'r2')
    #     # self.assertListEqual(data, [
    #     #     {
    #     #         '_id': str(col1_id1),
    #     #         'x1': 0.5,
    #     #         'x2': ['2016-01-02T03:04:05', '2016-02-03T04:05:06', '2016-03-04T05:06:07'],
    #     #         'x3': [123, 'foo'],
    #     #         'x4': {'a': 1, 'b': 2}
    #     #     }, {
    #     #         '_id': str(col1_id2),
    #     #         'x1': 1.5,
    #     #         'x2': ['2016-04-05T06:07:08', '2016-05-06T07:08:09', '2016-06-07T08:09:10'],
    #     #         'x3': [45601, 'bar'],
    #     #         'x4': {'a': 3, 'b': 4}
    #     #     }
    #     # ])
    #
    #
    #     # self.assertDictEqual(data, {
    #     #     '_id': str(col1_id1),
    #     #     'x1': 0.5,
    #     #     'x2': ["2016-01-02T03:04:05", "2016-02-03T04:05:06", "2016-03-04T05:06:07"],
    #     #     'x3': [123, "foo"],
    #     #     'x4': {"a": 1, "b": 2}
    #     # })
    #     #
    #     # data = yield x.to_json('r2', tz_name='Asia/Novosibirsk')
    #     # self.assertDictEqual(data, {
    #     #     'x2': ['2016-01-02T09:04:05+06:00', '2016-02-03T10:05:06+06:00', '2016-03-04T11:06:07+06:00'],
    #     #     'x3': [123, "foo"],
    #     #     'x4': {"a": 1, "b": 2}
    #     # })
    #     #
    #     # data = yield x.to_json('r3', 'r4')
    #     # self.assertDictEqual(data, {
    #     #     'a1': 0.5,
    #     #     'a2': 2.5,
    #     #     'a3': 1.0,
    #     #     'prop1': 2.5,
    #     #     'prop2': 1.0
    #     # })
    #     #
    #     # data = yield x.to_json('r5')
    #     # print data
    #     # self.assertDictEqual(data, {
    #     #     'x3.1': 'foo',
    #     #     'x4.a': 1,
    #     #     'x4.b': 2
    #     # })
    #
#     @gen_test
#     def test_from_json_1(self):
#         data = self.data1_b.copy()
#         x = yield TestClass1.from_json(data)
#         self.assertFalse(x.dirty)
#
#     @gen_test
#     def test_from_json_2(self):
#         data = self.data1_b.copy()
#         data['f_0'] = 'foo'
#         x = yield TestClass1.from_json(data)
#         self.assertTrue(x.dirty)
#         self.assertDictEqual(x._data.query, {'$set': {'f_0': 'foo'}})
#
#     @gen_test
#     def test_distinct(self):
#         x = yield TestClass1.distinct('f_0')
#         self.assertListEqual(x, [self.data1_a['f_0'], self.data1_b['f_0']])
#
#         x = yield TestClass1.distinct('f_0', {'f_1': self.data1_a['f_1']})
#         self.assertListEqual(x, [self.data1_a['f_0']])
#
#     @gen_test
#     def test_cls1(self):
#         x = yield TestClass2.find_one(self._id2_a)
#         self.assertEqual(x.pk, self._id2_a)
#         self._check_data(x, self.data2_a)
#
#         self.assertEqual(x['f_11'].dbref, self.data2_a['f_11'])
#         self.assertEqual(x['f_12'][0].dbref, self.data2_a['f_12'][0])
#         self.assertEqual(x['f_12'][1].dbref, self.data2_a['f_12'][1])
#
#         self.assertEqual(x['f_13'][0], self.data2_a['f_13'][0])
#         self.assertEqual(x['f_13'][1].dbref, self.data2_a['f_13'][1])
#
#     @gen_test
#     def test_cls2(self):
#         x = yield TestClass2.find_one(self._id2_a)
#         yield x.preload('f_13')
#
#         self.assertEqual(x.pk, self._id2_a)
#         self._check_data(x, self.data2_a)
#
#         self.assertEqual(x['f_11'].dbref, self.data2_a['f_11'])
#         self.assertEqual(x['f_12'][0].dbref, self.data2_a['f_12'][0])
#         self.assertEqual(x['f_12'][1].dbref, self.data2_a['f_12'][1])
#
#         self.assertEqual(x['f_13'][0], self.data2_a['f_13'][0])
#         self.assertDictEqual(x['f_13'][1].value()._data.value(), self.data1_b)
#
#     @gen_test
#     def test_cls3(self):
#         x = yield TestClass2.find_one(self._id2_a)
#         yield x.preload('f_11', 'f_12', 'f_13')
#
#         self.assertEqual(x.pk, self._id2_a)
#         self._check_data(x, self.data2_a)
#
#         self.assertEqual(x['f_11'].dbref, self.data2_a['f_11'])
#         self.assertDictEqual(x['f_11'].value()._data.value(), self.data1_a)
#         self.assertEqual(x['f_12'][0].dbref, self.data2_a['f_12'][0])
#         self.assertEqual(x['f_12'][1].dbref, self.data2_a['f_12'][1])
#         self.assertDictEqual(x['f_12'][0].value()._data.value(), self.data1_b)
#         self.assertDictEqual(x['f_12'][1].value()._data.value(), self.data1_a)
#
#         self.assertEqual(x['f_13'][0], self.data2_a['f_13'][0])
#         self.assertDictEqual(x['f_13'][1].value()._data.value(), self.data1_b)
#
#     @gen_test
#     def test_cls4(self):
#         x = yield TestClass2.find_one(self._id2_a, preload=True)
#
#         self.assertEqual(x.pk, self._id2_a)
#         self._check_data(x, self.data2_a)
#
#         self.assertEqual(x['f_11'].dbref, self.data2_a['f_11'])
#         self.assertDictEqual(x['f_11'].value()._data.value(), self.data1_a)
#
#         self.assertEqual(x['f_12'][0].dbref, self.data2_a['f_12'][0])
#         self.assertEqual(x['f_12'][1].dbref, self.data2_a['f_12'][1])
#         self.assertDictEqual(x['f_12'][0].value()._data.value(), self.data1_b)
#         self.assertDictEqual(x['f_12'][1].value()._data.value(), self.data1_a)
#
#         self.assertEqual(x['f_13'][0], self.data2_a['f_13'][0])
#         self.assertDictEqual(x['f_13'][1].value()._data.value(), self.data1_b)
#
#     @gen_test
#     def test_cls5(self):
#         x = (yield TestClass2.find(self._id2_a, preload=True))[0]
#
#         self.assertEqual(x.pk, self._id2_a)
#         self._check_data(x, self.data2_a)
#
#         self.assertEqual(x['f_11'].dbref, self.data2_a['f_11'])
#         self.assertDictEqual(x['f_11'].value()._data.value(), self.data1_a)
#
#         self.assertEqual(x['f_12'][0].dbref, self.data2_a['f_12'][0])
#         self.assertEqual(x['f_12'][1].dbref, self.data2_a['f_12'][1])
#         self.assertDictEqual(x['f_12'][0].value()._data.value(), self.data1_b)
#         self.assertDictEqual(x['f_12'][1].value()._data.value(), self.data1_a)
#
#         self.assertEqual(x['f_13'][0], self.data2_a['f_13'][0])
#         self.assertDictEqual(x['f_13'][1].value()._data.value(), self.data1_b)
#
#     @gen_test
#     def test_cls_json1(self):
#         x = yield TestClass2.find_one(self._id2_a, preload=True)
#         data1 = yield x.to_json('role_3')
#         data2 = {
#             'f_11': {
#                 '_id': str(self._id1_a),
#                 'f_0': self.data1_a['f_0'],
#                 'f_1': self.data1_a['f_1'],
#             }
#         }
#         self.assertDictEqual(data1, data2)
#
#         data1 = yield x.to_json('role_4')
#         data2 = {
#             # '_id': str(self._id2_a),
#             'f_12.0': {
#                 '_id': str(self._id1_b),
#                 'f_0': self.data1_b['f_0'],
#                 'f_1': self.data1_b['f_1']
#             },
#             'f_13.1.f_0': self.data1_b['f_0']
#         }
#         self.assertDictEqual(data1, data2)
#
#     @gen_test
#     def test_cls_save_1(self):
#         x = yield TestClass2.find_one(self._id2_a, preload=True)
#         self.assertFalse(x.dirty)
#         self.assertFalse(x['f_11'].dirty)
#         n = random_int()
#         x['f_11']['f_0'] = n
#         self.assertFalse(x.dirty)
#         self.assertTrue(x['f_11'].dirty)
#         self.assertEqual(x['f_11'].query, {'$set': {'f_0': n}})
#         yield x['f_11'].save()
#         self.assertFalse(x.dirty)
#         self.assertFalse(x['f_11'].dirty)
#         self.assertEqual(x['f_11.f_0'], n)
#         data = yield self.db[TEST_COLLECTION1].find_one(self._id1_a)
#         self.assertEqual(data['f_0'], n)
#
#     @gen_test
#     def test_cls_save_2(self):
#         data = self.data1_b.copy()
#         del data['_id']
#         x1 = TestClass1(data)
#         self.assertIsNone(x1.pk)
#         self.assertTrue(x1.dirty)
#         data['_id'] = None
#         self.assertDictEqual(x1._data.value(), data)
#         yield x1.save()
#         data['_id'] = x1.pk
#
#         x2 = yield TestClass2.find_one(self._id2_a, preload=True)
#         x2['f_11'] = x1
#         self.assertFalse(x1.dirty)
#         self.assertTrue(x2.dirty)
#         dbref = DBRef(TEST_COLLECTION1, x1.pk)
#         self.assertEqual(x2._data.query, {'$set': {'f_11': dbref}})
#
#         yield x2.save()
#         self.assertFalse(x1.dirty)
#         self.assertFalse(x2.dirty)
#
#         x3 = yield TestClass2.find_one(self._id2_a)
#         self.assertEqual(x3['f_11'].dbref, dbref)
#
#         yield x3.preload('f_11')
#         self.assertDictEqual(x3['f_11'].value()._data.value(), data)
#
#     @gen_test
#     def test_cls_save_3(self):
#         x1 = yield TestClass2.find_one(self._id2_a)
#         self.assertIsNotNone(x1['f_11'].value())
#         del x1['f_11']
#         self.assertIsNone(x1['f_11'].value())
#         self.assertTrue(x1.dirty)
#         self.assertEqual(x1._data.query, {'$unset': {'f_11': ''}})
#         yield x1.save()
#
#         x2 = yield TestClass2.find_one(self._id2_a, preload=True)
#         self.assertIsNone(x2['f_11'].value())
#
#     @gen_test
#     def test_sub_cls1(self):
#         data1 = {'_id': ObjectId, 'f_1': str}
#         self.assertDictEqual(TestClass3A.fields, data1)
#
#         data2 = data1.copy()
#         data2['f_2'] = int
#         self.assertDictEqual(TestClass3B.fields, data2)
#         self.assertEqual(TestClass3B.__collection__, TEST_COLLECTION3B)
#
#         data3 = data1.copy()
#         data3['f_3'] = float
#         self.assertDictEqual(TestClass3C.fields, data3)
#         self.assertEqual(TestClass3C.__collection__, TEST_COLLECTION3A)
#
#     @gen_test
#     def test_sub_cls2(self):
#         xb1 = TestClass3B(f_1=random_str(), f_2=random_int())
#         yield xb1.save()
#         x4 = TestClass4(x_1=xb1)
#         self.assertDictEqual(x4._data.query, {'$set': {'x_1': xb1.dbref}})
#         self.assertEqual(x4['x_1.f_1'], xb1['f_1'])
#
#         xb2 = TestClass3B(f_1=random_str(), f_2=random_int())
#         yield xb2.save()
#         x4 = TestClass4(x_1=xb2.dbref)
#         self.assertDictEqual(x4._data.query, {'$set': {'x_1': xb2.dbref}})
#         with self.assertRaises(ValueError):
#             _ = x4['x_1.f_1']
#         yield x4.preload('x_1')
#         self.assertEqual(x4['x_1.f_1'], xb2['f_1'])
#
#         xc = TestClass3C(f_1=random_str(), f_3=random_float())
#         yield xc.save()
#         x4 = TestClass4(x_1=xc)
#         self.assertDictEqual(x4._data.query, {'$set': {'x_1': xc.dbref}})
#         self.assertEqual(x4['x_1.f_1'], xc['f_1'])
#
#     @gen_test
#     def test_ruler_None(self):
#         x = yield TestClass2.find_one(self._id2_a)
#         self.assertIsNotNone(x['f_11'].value())
#         x['f_11'] = None
#         self.assertDictEqual(x._data.query, {'$set': {'f_11': None}})
#
#     @gen_test
#     def test_ruler_inc(self):
#         x = yield TestClass2.find_one(self._id2_a)
#         v1 = x['f_2'].value()
#         x['f_2'] += 10
#         self.assertEqual(x['f_2'].value(), v1 + 10)
#
#
# # TODO: add test  "res = yield foo.save()"
# # TODO: add test  "Documents.remove()"
# # TODO: add test  "Documents.filter(...)"
# # TODO: add test  "Document.reread(...)"
# # TODO: add test  "Documents.reread(...)"
