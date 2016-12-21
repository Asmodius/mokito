# coding: utf-8

import datetime

from bson import ObjectId
from bson.errors import InvalidId
from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, gen_test

import mokito

from tests.util import (
    TEST_DB_NAME,
    TEST_COLLECTION1,
    TEST_COLLECTION2,
    col1_id1,
    col1_dbref1,
    col1_data1,
    col1_id2,
    col1_dbref2,
    col1_data2,
    col2_id1,
    col2_data1,
    col2_data2,
    Document1,
    Document2
)


class ORMTestCase(AsyncTestCase):
    def get_new_ioloop(self):
        return IOLoop.instance()

    @gen_test
    def _init_collection(self):
        yield self.db[TEST_COLLECTION1].insert([col1_data1, col1_data2], safe=False)
        yield self.db[TEST_COLLECTION2].insert([col2_data1, col2_data2], safe=False)

    def setUp(self):
        super(ORMTestCase, self).setUp()
        self.db = mokito.ModelManager.databases[TEST_DB_NAME]
        self._init_collection()

    @gen_test
    def tearDown(self):
        yield self.db.command('drop', TEST_COLLECTION2, safe=False)
        yield self.db.command('drop', TEST_COLLECTION1, safe=False)
        super(ORMTestCase, self).tearDown()

    # def test_databases(self):
    #     self.assertIsInstance(mokito.ModelManager.databases[TEST_DB_NAME], mokito.Client)
    #
    # @gen_test
    # def test_find_one_1(self):
    #     x = yield Document1.find_one(col1_id1)
    #     self.assertEqual(x._id, col1_id1)
    #     y = yield Document1.by_id(col1_id1)
    #     self.assertEqual(y._id, col1_id1)
    #
    #     data = col1_data1.copy()
    #     data.pop('_id')
    #     self.assertDictEqual(data, x.value)
    #     self.assertDictEqual(data, y.value)
    #
    #     x = yield Document1.find_one(col1_id2)
    #     y = yield Document1.by_id(col1_id2)
    #     self.assertEqual(x._id, col1_id2)
    #     self.assertEqual(y._id, col1_id2)
    #     data = col1_data2.copy()
    #     data.pop('_id')
    #     data.pop('foo')
    #     self.assertDictEqual(data, x.value)
    #     self.assertDictEqual(data, y.value)
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
    #     self.assertDictEqual(x.query, {'$set': {'x1': 3.0}})
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
    #     x = Document1(data, inner=True)
    #     self.assertIsNone(x._id)
    #     self.assertTrue(x.dirty)
    #     self.assertDictEqual(x.value, data)
    #
    #     y = yield x.save()
    #     self.assertTrue(y)
    #     self.assertIsNotNone(x._id)
    #     self.assertFalse(x.dirty)
    #
    #     data = yield self.db[TEST_COLLECTION1].find_one(x._id)
    #     del data['_id']
    #     self.assertDictEqual(x.value, data)
    #     self.assertEqual((yield self.db[TEST_COLLECTION1].count()), 3)
    #
    # @gen_test
    # def test_load_1(self):
    #     d = yield Document2.find_one(col2_id1)
    #     self.assertDictEqual(d['d1'].value, {'x2': [], 'x3': [None, None], 'x1': None, 'x4': {'a': None, 'b': None}})
    #     self.assertEqual(d['d1'].dbref, col1_dbref1)
    #
    #     yield d['d1'].reread()
    #     self.assertDictEqual(d['d1'].value, {
    #         'x1': 0.5,
    #         'x2': [datetime.datetime(2016, 1, 2, 3, 4, 5),
    #                datetime.datetime(2016, 2, 3, 4, 5, 6),
    #                datetime.datetime(2016, 3, 4, 5, 6, 7)],
    #         'x3': [123, 'z1'],
    #         'x4': {'a': 1, 'b': 2}
    #     })
    #
    # @gen_test
    # def test_load_2(self):
    #     d = yield Document2.find()
    #
    #     self.assertDictEqual(d['0.d1'].value, {'x2': [], 'x3': [None, None], 'x1': None, 'x4': {'a': None, 'b': None}})
    #     self.assertEqual(d['0.d1'].dbref, col1_dbref1)
    #     yield d['0.d1'].reread()
    #     self.assertDictEqual(d['0.d1'].value, {
    #         'x1': 0.5,
    #         'x2': [datetime.datetime(2016, 1, 2, 3, 4, 5),
    #                datetime.datetime(2016, 2, 3, 4, 5, 6),
    #                datetime.datetime(2016, 3, 4, 5, 6, 7)],
    #         'x3': [123, 'z1'],
    #         'x4': {'a': 1, 'b': 2}
    #     })
    #
    # @gen_test
    # def test_to_prop(self):
    #     x = yield Document1.find_one(col1_id1)
    #     self.assertEqual(x.prop1, x['x1'].value + 2)
    #     self.assertEqual(x.prop2, x['x1'].value * 2)
    #     x['x1'] = 10
    #     self.assertEqual(x.prop1, 12.0)
    #     self.assertEqual(x.prop2, 20.0)

    @gen_test
    def test_to_json_1(self):
        d = yield Document1.find_one(col1_id1)

        data = d.get('id', 'x1', 'x2', 'x3', 'x4', date_format='iso', as_json=True)
        self.assertDictEqual(data, {
            'id': str(col1_id1),
            'x1': 0.5,
            'x2': ["2016-01-02T03:04:05", "2016-02-03T04:05:06", "2016-03-04T05:06:07"],
            'x3': [123, 1],
            'x4': {"a": 1, "b": 2}
        })

        data = d.get('x2', 'x3', 'x4', date_format='iso', tz_name='Asia/Novosibirsk')
        self.assertDictEqual(data, {
            'x2': ['2016-01-02T09:04:05+06:00', '2016-02-03T10:05:06+06:00', '2016-03-04T11:06:07+06:00'],
            'x3': [123, 1],
            'x4': {"a": 1, "b": 2}
        })

        data = d.get('x1', 'prop1', 'prop2')
        self.assertDictEqual(data, {
            'x1': 0.5,
            'prop1': 2.5,
            'prop2': 1.0
        })

    @gen_test
    def test_to_json_2(self):
        d = yield Document1.find()

        data = d.get('id', 'x1', 'x2', 'x3', 'x4', date_format='iso', as_json=True)
        self.assertListEqual(data, [
            {
                'id': str(col1_id1),
                'x1': 0.5,
                'x2': ['2016-01-02T03:04:05', '2016-02-03T04:05:06', '2016-03-04T05:06:07'],
                'x3': [123, 1],
                'x4': {'a': 1, 'b': 2}
            }, {
                'id': str(col1_id2),
                'x1': 1.5,
                'x2': ['2016-04-05T06:07:08', '2016-05-06T07:08:09', '2016-06-07T08:09:10'],
                'x3': [45601, 2],
                'x4': {'a': 3, 'b': 4}
            }
        ])

        data = d.get('x2', tz_name='Asia/Novosibirsk')
        self.assertListEqual(data, [
            {'x2': ['2016-01-02T09:04:05+06:00', '2016-02-03T10:05:06+06:00', '2016-03-04T11:06:07+06:00']},
            {'x2': ['2016-04-05T12:07:08+06:00', '2016-05-06T13:08:09+06:00', '2016-06-07T14:09:10+06:00']}
        ])

        data = d.get('x1', 'prop1', 'prop2')
        self.assertListEqual(data, [
            {'x1': 0.5, 'prop1': 2.5, 'prop2': 1.0},
            {'x1': 1.5, 'prop1': 3.5, 'prop2': 3.0}
        ])

    @gen_test
    def test_to_json_3(self):
        d = yield Document1.find()
        data = d.get('id', 'x1')
        self.assertListEqual(data, [{'id': str(col1_id1), 'x1': 0.5},
                                    {'id': str(col1_id2), 'x1': 1.5}])

    @gen_test
    def test_from_json_1(self):
        d = Document2()
        self.assertFalse(d.dirty)
        d.set(col2_data2, inner=True)
        self.assertTrue(d.dirty)
        self.assertEqual(d['d1'].dbref, col1_dbref2)

        yield d['d1'].reread()
        yield [i.reread() for i in d['d2']]
        dt1 = datetime.datetime(2015, 1, 2, 3, 4, 5)
        dt2 = datetime.datetime(2015, 2, 3, 4, 5, 6)
        dt3 = datetime.datetime(2015, 3, 4, 5, 6, 7)
        dt4 = datetime.datetime(2016, 4, 5, 6, 7, 8)
        dt5 = datetime.datetime(2016, 5, 6, 7, 8, 9)
        dt6 = datetime.datetime(2016, 6, 7, 8, 9, 10)
        self.assertDictEqual(d.value, {
            'f1': [45602, 'foo3'],
            'f2': {'a': 11, 'b': 12},
            'm1': {
                'x1': 0.2,
                'x2': [datetime.datetime(2016, 11, 12, 13, 14, 15), datetime.datetime(2016, 12, 13, 14, 15, 16)],
                'x3': [7, 'z3'],
                'x4': {'a': 8, 'b': 8}
            },
            'm2': [
                {'x2': [dt1], 'x3': [8, 'z1'], 'x1': 0.2, 'x4': {'a': 9, 'b': 9}},
                {'x2': [dt2, dt3], 'x3': [9, 'z2'], 'x1': 0.3, 'x4': {'a': 10, 'b': 10}}
            ],
            'd1': {
                'x1': 1.5,
                'x2': [dt4, dt5, dt6],
                'x3': [45601, 'z2'],
                'x4': {'a': 3, 'b': 4}
            },
            'd2': [
                {
                    'x1': 1.5,
                    'x2': [dt4, dt5, dt6],
                    'x3': [45601, 'z2'],
                    'x4': {'a': 3, 'b': 4}
                }
            ]
        })

    @gen_test
    def test_distinct(self):
        data = yield Document2.distinct('m1.x1')
        self.assertListEqual(data, [0.1, 0.2])
