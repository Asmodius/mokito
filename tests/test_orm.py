import copy

from bson import ObjectId
from bson.errors import InvalidId
from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, gen_test
from tornado.gen import coroutine
import motor.motor_tornado

import mokito

import tests.util as u


class ORMTestCase(AsyncTestCase):
    def get_new_ioloop(self):
        return IOLoop.instance()

    @coroutine
    def _init_collection(self):
        yield self.db[u.TEST_COLLECTION1].insert_many([u.col1_data1, u.col1_data2])
        yield self.db[u.TEST_COLLECTION2].insert_many([u.col2_data1, u.col2_data2])
        yield self.db[u.TEST_COLLECTION3].insert_many([u.col3_data1, u.col3_data2])

    @coroutine
    def _drop_collection(self):
        yield self.db.drop_collection(u.TEST_COLLECTION3)
        yield self.db.drop_collection(u.TEST_COLLECTION2)
        yield self.db.drop_collection(u.TEST_COLLECTION1)

    def setUp(self):
        super(ORMTestCase, self).setUp()
        self.setUpHelper()

    @gen_test
    def setUpHelper(self):
        self.db = motor.motor_tornado.MotorClient(u.TEST_DB_URI)[u.TEST_DB_NAME]
        yield self._drop_collection()
        yield self._init_collection()

    def tearDown(self):
        yield self.tearDownHelper()
        super(ORMTestCase, self).tearDown()

    @gen_test
    def tearDownHelper(self):
        yield self._drop_collection()

    @gen_test
    def test_find_one_1(self):
        x = yield u.Document1.find_one(u.col1_id1)
        self.assertEqual(x.id, u.col1_id1)

        data = copy.deepcopy(u.col1_data1)
        data['x3'][1] = 1
        self.assertDictEqual(data, x.value)

        x = yield u.Document1.find_one(u.col1_id2)
        self.assertEqual(x.id, u.col1_id2)
        data = copy.deepcopy(u.col1_data2)
        data.pop('foo')
        data['x3'][1] = 2
        self.assertDictEqual(data, x.value)

    @gen_test
    def test_find_one_2(self):
        _id = ObjectId()
        x = yield u.Document1.find_one(_id)
        self.assertIsNone(x)

        with self.assertRaises(InvalidId):
            yield u.Document1.find_one('foo')

    @gen_test
    async def test_find_1(self):
        x = await u.Document1.find().all()
        self.assertEqual(len(x), 2)

        data = copy.deepcopy(u.col1_data1)
        data['x3'][1] = 1
        self.assertDictEqual(data, x[0].value)

        data = copy.deepcopy(u.col1_data2)
        data.pop('foo')
        data['x3'][1] = 2
        self.assertDictEqual(data, x[1].value)

    @gen_test
    async def test_find_2(self):
        x = []
        async for i in u.Document1.find():
            x.append(i)
        self.assertEqual(len(x), 2)

        data = copy.deepcopy(u.col1_data1)
        data['x3'][1] = 1
        self.assertDictEqual(data, x[0].value)

        data = copy.deepcopy(u.col1_data2)
        data.pop('foo')
        data['x3'][1] = 2
        self.assertDictEqual(data, x[1].value)

    @gen_test
    def test_count(self):
        self.assertEqual((yield u.Document1.count()), 2)

    @gen_test
    def test_save_1(self):
        x = yield u.Document1.find_one(u.col1_id2)
        self.assertFalse(x.dirty)
        x['x1'].value = 3
        self.assertTrue(x.dirty)
        self.assertDictEqual(x.query, {'$set': {'x1': 3.0}})
        y = yield x.save()
        self.assertTrue(y)
        self.assertFalse(x.dirty)

        data = yield self.db[u.TEST_COLLECTION1].find_one(u.col1_id2, ['x1'])
        self.assertEqual(data['x1'], 3.0)
        self.assertEqual(x['x1'].value, 3.0)

        data = yield self.db[u.TEST_COLLECTION1].count()
        self.assertEqual(data, 2)

    @gen_test
    def test_save_2(self):
        data = copy.deepcopy(u.col1_data1)
        del data['_id']

        x = u.Document1(data, inner=True)
        self.assertIsNone(x.id)
        self.assertTrue(x.dirty)
        data['x3'][1] = 1
        data['_id'] = None
        self.assertDictEqual(x.value, data)

        y = yield x.save()
        self.assertTrue(y)
        self.assertIsNotNone(x.id)
        self.assertFalse(x.dirty)

        data = yield self.db[u.TEST_COLLECTION1].find_one(x.id)
        data['x3'][1] = 1
        self.assertDictEqual(x.value, data)
        self.assertEqual((yield self.db[u.TEST_COLLECTION1].count()), 3)

    @gen_test
    def test_save_3(self):
        x = u.Document2()

        self.assertIsNone(x.id)
        self.assertEqual((yield self.db[u.TEST_COLLECTION2].count()), 2)

        res = yield x.save()
        self.assertTrue(res)
        self.assertDictEqual(x.value, {
            '_id': x.id,
            'f1': [None, None],
            'f2': {'a': None, 'b': None},
            'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
            'm2': [],
            'd1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}, '_id': None},
            'd2': []
        })
        self.assertIsNotNone(x.id)
        self.assertEqual((yield self.db[u.TEST_COLLECTION2].count()), 3)

        res = yield self.db[u.TEST_COLLECTION2].find_one({'_id': {'$nin': [u.col2_id1, u.col2_id2]}})
        self.assertDictEqual(res, {
            '_id': x.id,
            'f1': [None, None],
            'f2': {'a': None, 'b': None},
            'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
            'm2': [],
            'd1': None,
            'd2': []
        })

    @gen_test
    def test_save_4(self):
        x = u.Document2()
        x['f1.1'].value = 'foo'
        x['f2.a'].value = 123

        self.assertIsNone(x.id)
        self.assertEqual((yield self.db[u.TEST_COLLECTION2].count()), 2)

        res = yield x.save()
        self.assertTrue(res)
        self.assertDictEqual(x.value, {
            '_id': x.id,
            'f1': [None, 'foo'],
            'f2': {'a': 123, 'b': None},
            'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
            'm2': [], 'd1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}, '_id': None},
            # 'd1': {'_id': None, 'x2': [], 'x3': [None, None], 'x1': None, 'x4': {'a': None, 'b': None}},
            'd2': []
        })
        self.assertIsNotNone(x.id)
        self.assertEqual((yield self.db[u.TEST_COLLECTION2].count()), 3)

        res = yield self.db[u.TEST_COLLECTION2].find_one({'_id': {'$nin': [u.col2_id1, u.col2_id2]}})
        self.assertDictEqual(res, {
            '_id': x.id,
            'f1': [None, 'foo'],
            'f2': {'a': 123, 'b': None},
            'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
            'm2': [],
            'd1': None,
            'd2': []
        })

    @gen_test
    def test_load_1(self):
        d = yield u.Document2.find_one(u.col2_id1)
        self.assertDictEqual(d['d1'].value, {
            '_id': u.col1_id1,
            'x2': [],
            'x3': [None, None],
            'x1': None,
            'x4': {'a': None, 'b': None}
        })
        self.assertEqual(d['d1'].dbref, u.col1_dbref1)

        yield d['d1'].reload()
        self.assertDictEqual(d['d1'].value, {
            '_id': u.col1_id1,
            'x1': 0.5,
            'x2': [u.dt1, u.dt2, u.dt3],
            'x3': [123, 1],
            'x4': {'a': 1, 'b': 2}
        })

    @gen_test
    def test_load_2(self):
        d = yield u.Document2.find().all()

        self.assertDictEqual(d['0.d1'].value, {
            '_id': u.col1_id1,
            'x2': [],
            'x3': [None, None],
            'x1': None,
            'x4': {'a': None, 'b': None}
        })
        self.assertEqual(d['0.d1'].dbref, u.col1_dbref1)
        yield d['0.d1'].reload()
        self.assertDictEqual(d['0.d1'].value, {
            '_id': u.col1_id1,
            'x1': 0.5,
            'x2': [u.dt1, u.dt2, u.dt3],
            'x3': [123, 1],
            'x4': {'a': 1, 'b': 2}
        })

    @gen_test
    def test_to_prop(self):
        x = yield u.Document1.find_one(u.col1_id1)
        self.assertEqual(x.prop1, x['x1'].value + 2)
        self.assertEqual(x.prop2, x['x1'].value * 2)
        x['x1'].value = 10
        self.assertEqual(x.prop1, 12.0)
        self.assertEqual(x.prop2, 20.0)

    @gen_test
    def test_to_json_1(self):
        d = yield u.Document1.find_one(u.col1_id1)

        data = d.get_value(_date_format='iso', _format='json')
        self.assertDictEqual(data, {
            '_id': u.col1_id1,
            'x1': 0.5,
            'x2': ["2016-01-02T03:04:05", "2016-02-03T04:05:06", "2016-03-04T05:06:07"],
            'x3': [123, 1],
            'x4': {"a": 1, "b": 2}
        })

        data = d.get_value(_date_format='iso', tz_name='Asia/Novosibirsk')
        self.assertDictEqual(data, {
            '_id': u.col1_id1,
            'x1': 0.5,
            'x2': ['2016-01-02T09:04:05+06:00', '2016-02-03T10:05:06+06:00', '2016-03-04T11:06:07+06:00'],
            'x3': [123, 1],
            'x4': {"a": 1, "b": 2}
        })

    @gen_test
    def test_to_json_2(self):
        d = yield u.Document1.find().all()

        data = d.get_value(_date_format='iso', _format='json')
        self.assertListEqual(data, [
            {
                '_id': u.col1_id1,
                'x1': 0.5,
                'x2': ['2016-01-02T03:04:05', '2016-02-03T04:05:06', '2016-03-04T05:06:07'],
                'x3': [123, 1],
                'x4': {'a': 1, 'b': 2}
            }, {
                '_id': u.col1_id2,
                'x1': 1.5,
                'x2': ['2016-04-05T06:07:08', '2016-05-06T07:08:09', '2016-06-07T08:09:10'],
                'x3': [45601, 2],
                'x4': {'a': 3, 'b': 4}
            }
        ])

    @gen_test
    def test_from_json_1(self):
        d = u.Document2()
        self.assertFalse(d.dirty)
        d.set_value(u.col2_data2, inner=True)
        self.assertTrue(d.dirty)
        self.assertEqual(d['d1'].dbref, u.col1_dbref2)

        yield d['d1'].reload()
        yield [i.reload() for i in d['d2']]
        self.assertDictEqual(d.value, {
            '_id': u.col2_id2,
            'f1': [45602, 'foo3'],
            'f2': {'a': 11, 'b': 12},
            'm1': {
                'x1': 0.2,
                'x2': [u.dt11, u.dt12],
                'x3': [7, 3],
                'x4': {'a': 8, 'b': 8}
            },
            'm2': [
                {'x1': 0.2, 'x2': [u.xt1], 'x3': [8, 1], 'x4': {'a': 9, 'b': 9}},
                {'x1': 0.3, 'x2': [u.xt2, u.xt3], 'x3': [9, 2], 'x4': {'a': 10, 'b': 10}}],
            'd1': {'x1': 1.5, 'x2': [u.dt4, u.dt5, u.dt6], 'x3': [45601, 2], 'x4': {'a': 3, 'b': 4}, '_id': u.col1_id2},
            'd2': [{'x1': 1.5, 'x2': [u.dt4, u.dt5, u.dt6], 'x3': [45601, 2], 'x4': {'a': 3, 'b': 4}, '_id': u.col1_id2}]
        })

    @gen_test
    def test_distinct(self):
        data = yield u.Document2.distinct('m1.x1')
        self.assertListEqual(data, [0.1, 0.2])

    @gen_test
    def test_set_document(self):
        x1 = yield u.Document1.find_one(u.col1_id2)
        x2 = yield u.Document2.find_one(u.col2_id1)

        yield x2.reload('d1')
        self.assertDictEqual(x2['d1'].value, {
            '_id': u.col1_id1,
            'x1': 0.5,
            'x2': [u.dt1, u.dt2, u.dt3],
            'x3': [123, 1],
            'x4': {'a': 1, 'b': 2}
        })

        x2['d1'] = x1
        self.assertTrue(x2.dirty)
        self.assertDictEqual(x2.query, {'$set': {'d1': u.col1_dbref2}})

        yield x2.reload('d1')
        self.assertDictEqual(x2['d1'].value, {
            '_id': u.col1_id2,
            'x1': 1.5,
            'x2': [u.dt4, u.dt5, u.dt6],
            'x3': [45601, 2],
            'x4': {'a': 3, 'b': 4}
        })

    @gen_test
    def test_documents_1(self):
        x1 = yield u.Document1.find().all()
        self.assertEqual(len(x1), 2)
        for i in x1:
            self.assertIn(i.id, [u.col1_id1, u.col1_id2])

        yield x1.remove()

        x2 = yield u.Document1.find().all()
        self.assertEqual(len(x2), 0)

        yield x1.save()

        x2 = yield u.Document1.find().all()
        self.assertEqual(len(x2), 2)

    @gen_test
    def test_sort_1(self):
        x = [i['foo'].value for i in (yield u.Document3.find().all())]
        self.assertListEqual(x, [1, 2])

        x = [i['foo'].value for i in (yield u.Document4.find().all())]
        self.assertListEqual(x, [2, 1])

        x = [i['foo'].value for i in (yield u.Document4.find(sort='foo').all())]
        self.assertListEqual(x, [1, 2])

        x = [i['foo'].value for i in (yield u.Document4.find(sort=['-foo']).all())]
        self.assertListEqual(x, [2, 1])
