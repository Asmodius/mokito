# coding: utf-8

from bson import ObjectId, DBRef
from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, gen_test

from mokito.database import Database
from tests.util import (
    TEST_DB_NAME,
    TEST_COLLECTION1,
    TEST_COLLECTION2,
    TEST_COLLECTION3A,
    TEST_COLLECTION3B,
    TEST_COLLECTION4,
    TEST_COLLECTION5,
    random_int,
    random_str,
    random_float,
    random_datetime,
    TestClass1,
    TestClass2,
    TestClass3A,
    TestClass3B,
    TestClass3C,
    TestClass4,
    data1_a,
    data1_b,
    data2_a,
    data2_b
)


class ORMTestCase(AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super(ORMTestCase, self).__init__(*args, **kwargs)
        self._id1_a = ObjectId()
        self.ref_a = DBRef(TEST_COLLECTION1, self._id1_a)
        self.data1_a = data1_a.copy()
        self.data1_a['_id'] = self._id1_a

        self._id1_b = ObjectId()
        self.ref_b = DBRef(TEST_COLLECTION1, self._id1_b)
        self.data1_b = data1_b.copy()
        self.data1_b['_id'] = self._id1_b

        self._id2_a = ObjectId()
        self.data2_a = data2_a.copy()
        self.data2_a['_id'] = self._id2_a
        self.data2_a['f_11'] = self.ref_a
        self.data2_a['f_12'] = [self.ref_a, self.ref_b]
        self.data2_a['f_13'] = [random_int(), self.ref_a]

        self._id2_b = ObjectId()
        self.data2_b = data2_b.copy()
        self.data2_b['_id'] = self._id2_b
        self.data2_b['f_11'] = self.ref_b
        self.data2_a['f_12'] = [self.ref_b, self.ref_a]
        self.data2_a['f_13'] = [random_int(), self.ref_b]

    def get_new_ioloop(self):
        return IOLoop.instance()

    @gen_test
    def _init_collection(self):
        self.db = Database.get(TEST_DB_NAME)
        yield self.db[TEST_COLLECTION1].insert([self.data1_a, self.data1_b])
        yield self.db[TEST_COLLECTION2].insert([self.data2_a, self.data2_b])

    def setUp(self):
        super(ORMTestCase, self).setUp()
        self._init_collection()

    @gen_test
    def tearDown(self):
        yield self.db.command('drop', TEST_COLLECTION2)
        yield self.db.command('drop', TEST_COLLECTION1)
        yield self.db.command('drop', TEST_COLLECTION3A)
        yield self.db.command('drop', TEST_COLLECTION3B)
        yield self.db.command('drop', TEST_COLLECTION4)
        yield self.db.command('drop', TEST_COLLECTION5)
        super(ORMTestCase, self).tearDown()

    def _check_data(self, obj, data):
        for i in ('f_0', 'f_1', 'f_2', 'f_3', 'f_4', 'f_5', 'f_6', 'f_7', 'f_8', 'f_10'):
            self.assertEqual(obj[i], data[i])

        self.assertEqual(obj['f_9'][0], data['f_9'][0])
        self.assertEqual(obj['f_9'][1], data['f_9'][1])
        self.assertIsNone(obj['foo'])

    def test_databases(self):
        self.assertEqual(Database.all_clients.keys()[0], TEST_DB_NAME)

    @gen_test
    def test_find_one(self):
        for _id, data in [(self._id2_a, self.data2_a), (self._id2_b, self.data2_b)]:
            x = yield TestClass2.find_one(_id)
            self.assertEqual(x.pk, _id)
            self._check_data(x, data)

    @gen_test
    def test_find(self):
        for x in (yield TestClass1.find()):
            data = self.data1_a if x.pk == self._id1_a else self.data1_b
            self.assertDictEqual(x._data.value(), data)

    @gen_test
    def test_count(self):
        self.assertEqual((yield TestClass1.count()), 2)

    @gen_test
    def test_save_1(self):
        n = random_datetime()
        x = yield TestClass1.find_one(self._id1_a)
        self.assertFalse(x.dirty)
        x['f_0'] = n
        self.assertTrue(x.dirty)
        yield x.save()
        self.assertFalse(x.dirty)

        data = yield self.db[TEST_COLLECTION1].find_one(self._id1_a)
        self.assertEqual(data['f_0'], n)
        self.assertEqual(x['f_0'].value(), n)

        data = yield self.db[TEST_COLLECTION1].count()
        self.assertEqual(data, 2)

    @gen_test
    def test_save_2(self):
        data = self.data1_a.copy()
        del data['_id']

        x = TestClass1(data)
        self.assertIsNone(x.pk)
        self.assertTrue(x.dirty)
        data['_id'] = None
        self.assertDictEqual(x._data.value(), data)

        yield x.save()
        self.assertIsNotNone(x.pk)
        self.assertFalse(x.dirty)
        data['_id'] = x.pk
        self.assertDictEqual(x._data.value(), data)

        data = yield self.db[TEST_COLLECTION1].find_one(x.pk)
        self.assertDictEqual(x._data.value(), data)

        data = yield self.db[TEST_COLLECTION1].count()
        self.assertEqual(data, 3)

    @gen_test
    def test_to_prop(self):
        x = yield TestClass1.find_one(self._id1_a)
        self.assertEqual(x.prop, '%s:%s' % (self.data1_a['f_1'], self.data1_a['f_0']))

    @gen_test
    def test_to_json_1(self):
        x = yield TestClass1.find_one(self._id1_a)
        data1 = yield x.to_json()
        data2 = self.data1_a.copy()
        data2['_id'] = str(data2['_id'])
        self.assertDictEqual(data1, data2)

    @gen_test
    def test_to_json_2(self):
        x = yield TestClass2.find_one(self._id2_a)

        data1 = yield x.to_json('role_1')
        data2 = {
            'f_0': self.data2_a['f_0'],
            'f_5': self.data2_a['f_5'].strftime("%B %d, %Y"),
            'prop': '%s:%s' % (self.data2_a['f_1'], self.data2_a['f_2'])
        }
        self.assertDictEqual(data1, data2)

        data1 = yield x.to_json('role_1')
        self.assertDictEqual(data1, data2)

    @gen_test
    def test_to_json_3(self):
        x = yield TestClass2.find_one(self._id2_a)

        data1 = yield x.to_json('role_2')
        data2 = {
            'f_7': self.data2_a['f_7'],
            'f_10.0': self.data2_a['f_10'][0],
            'f_6.f_6_1': self.data2_a['f_6']['f_6_1']
        }
        self.assertDictEqual(data1, data2)

        data1 = yield x.to_json('role_2')
        self.assertDictEqual(data1, data2)

    @gen_test
    def test_from_json_1(self):
        data = self.data1_b.copy()
        x = yield TestClass1.from_json(data)
        self.assertFalse(x.dirty)

    @gen_test
    def test_from_json_2(self):
        data = self.data1_b.copy()
        data['f_0'] = 'foo'
        x = yield TestClass1.from_json(data)
        self.assertTrue(x.dirty)
        self.assertDictEqual(x._data.query, {'$set': {'f_0': 'foo'}})

    @gen_test
    def test_distinct(self):
        x = yield TestClass1.distinct('f_0')
        self.assertListEqual(x, [self.data1_a['f_0'], self.data1_b['f_0']])

        x = yield TestClass1.distinct('f_0', {'f_1': self.data1_a['f_1']})
        self.assertListEqual(x, [self.data1_a['f_0']])

    @gen_test
    def test_cls1(self):
        x = yield TestClass2.find_one(self._id2_a)
        self.assertEqual(x.pk, self._id2_a)
        self._check_data(x, self.data2_a)

        self.assertEqual(x['f_11'].dbref, self.data2_a['f_11'])
        self.assertEqual(x['f_12'][0].dbref, self.data2_a['f_12'][0])
        self.assertEqual(x['f_12'][1].dbref, self.data2_a['f_12'][1])

        self.assertEqual(x['f_13'][0], self.data2_a['f_13'][0])
        self.assertEqual(x['f_13'][1].dbref, self.data2_a['f_13'][1])

    @gen_test
    def test_cls2(self):
        x = yield TestClass2.find_one(self._id2_a)
        yield x.preload('f_13')

        self.assertEqual(x.pk, self._id2_a)
        self._check_data(x, self.data2_a)

        self.assertEqual(x['f_11'].dbref, self.data2_a['f_11'])
        self.assertEqual(x['f_12'][0].dbref, self.data2_a['f_12'][0])
        self.assertEqual(x['f_12'][1].dbref, self.data2_a['f_12'][1])

        self.assertEqual(x['f_13'][0], self.data2_a['f_13'][0])
        self.assertDictEqual(x['f_13'][1].value()._data.value(), self.data1_b)

    @gen_test
    def test_cls3(self):
        x = yield TestClass2.find_one(self._id2_a)
        yield x.preload('f_11', 'f_12', 'f_13')

        self.assertEqual(x.pk, self._id2_a)
        self._check_data(x, self.data2_a)

        self.assertEqual(x['f_11'].dbref, self.data2_a['f_11'])
        self.assertDictEqual(x['f_11'].value()._data.value(), self.data1_a)
        self.assertEqual(x['f_12'][0].dbref, self.data2_a['f_12'][0])
        self.assertEqual(x['f_12'][1].dbref, self.data2_a['f_12'][1])
        self.assertDictEqual(x['f_12'][0].value()._data.value(), self.data1_b)
        self.assertDictEqual(x['f_12'][1].value()._data.value(), self.data1_a)

        self.assertEqual(x['f_13'][0], self.data2_a['f_13'][0])
        self.assertDictEqual(x['f_13'][1].value()._data.value(), self.data1_b)

    @gen_test
    def test_cls4(self):
        x = yield TestClass2.find_one(self._id2_a, preload=True)

        self.assertEqual(x.pk, self._id2_a)
        self._check_data(x, self.data2_a)

        self.assertEqual(x['f_11'].dbref, self.data2_a['f_11'])
        self.assertDictEqual(x['f_11'].value()._data.value(), self.data1_a)

        self.assertEqual(x['f_12'][0].dbref, self.data2_a['f_12'][0])
        self.assertEqual(x['f_12'][1].dbref, self.data2_a['f_12'][1])
        self.assertDictEqual(x['f_12'][0].value()._data.value(), self.data1_b)
        self.assertDictEqual(x['f_12'][1].value()._data.value(), self.data1_a)

        self.assertEqual(x['f_13'][0], self.data2_a['f_13'][0])
        self.assertDictEqual(x['f_13'][1].value()._data.value(), self.data1_b)

    @gen_test
    def test_cls5(self):
        x = (yield TestClass2.find(self._id2_a, preload=True))[0]

        self.assertEqual(x.pk, self._id2_a)
        self._check_data(x, self.data2_a)

        self.assertEqual(x['f_11'].dbref, self.data2_a['f_11'])
        self.assertDictEqual(x['f_11'].value()._data.value(), self.data1_a)

        self.assertEqual(x['f_12'][0].dbref, self.data2_a['f_12'][0])
        self.assertEqual(x['f_12'][1].dbref, self.data2_a['f_12'][1])
        self.assertDictEqual(x['f_12'][0].value()._data.value(), self.data1_b)
        self.assertDictEqual(x['f_12'][1].value()._data.value(), self.data1_a)

        self.assertEqual(x['f_13'][0], self.data2_a['f_13'][0])
        self.assertDictEqual(x['f_13'][1].value()._data.value(), self.data1_b)

    @gen_test
    def test_cls_json1(self):
        x = yield TestClass2.find_one(self._id2_a, preload=True)
        data1 = yield x.to_json('role_3')
        data2 = {
            'f_11': {
                '_id': str(self._id1_a),
                'f_0': self.data1_a['f_0'],
                'f_1': self.data1_a['f_1'],
            }
        }
        self.assertDictEqual(data1, data2)

        data1 = yield x.to_json('role_4')
        data2 = {
            # '_id': str(self._id2_a),
            'f_12.0': {
                '_id': str(self._id1_b),
                'f_0': self.data1_b['f_0'],
                'f_1': self.data1_b['f_1']
            },
            'f_13.1.f_0': self.data1_b['f_0']
        }
        self.assertDictEqual(data1, data2)

    @gen_test
    def test_cls_save_1(self):
        x = yield TestClass2.find_one(self._id2_a, preload=True)
        self.assertFalse(x.dirty)
        self.assertFalse(x['f_11'].dirty)
        n = random_int()
        x['f_11']['f_0'] = n
        self.assertFalse(x.dirty)
        self.assertTrue(x['f_11'].dirty)
        self.assertEqual(x['f_11'].query, {'$set': {'f_0': n}})
        yield x['f_11'].save()
        self.assertFalse(x.dirty)
        self.assertFalse(x['f_11'].dirty)
        self.assertEqual(x['f_11.f_0'], n)
        data = yield self.db[TEST_COLLECTION1].find_one(self._id1_a)
        self.assertEqual(data['f_0'], n)

    @gen_test
    def test_cls_save_2(self):
        data = self.data1_b.copy()
        del data['_id']
        x1 = TestClass1(data)
        self.assertIsNone(x1.pk)
        self.assertTrue(x1.dirty)
        data['_id'] = None
        self.assertDictEqual(x1._data.value(), data)
        yield x1.save()
        data['_id'] = x1.pk

        x2 = yield TestClass2.find_one(self._id2_a, preload=True)
        x2['f_11'] = x1
        self.assertFalse(x1.dirty)
        self.assertTrue(x2.dirty)
        dbref = DBRef(TEST_COLLECTION1, x1.pk)
        self.assertEqual(x2._data.query, {'$set': {'f_11': dbref}})

        yield x2.save()
        self.assertFalse(x1.dirty)
        self.assertFalse(x2.dirty)

        x3 = yield TestClass2.find_one(self._id2_a)
        self.assertEqual(x3['f_11'].dbref, dbref)

        yield x3.preload('f_11')
        self.assertDictEqual(x3['f_11'].value()._data.value(), data)

    @gen_test
    def test_cls_save_3(self):
        x1 = yield TestClass2.find_one(self._id2_a)
        self.assertIsNotNone(x1['f_11'].value())
        del x1['f_11']
        self.assertIsNone(x1['f_11'].value())
        self.assertTrue(x1.dirty)
        self.assertEqual(x1._data.query, {'$unset': {'f_11': ''}})
        yield x1.save()

        x2 = yield TestClass2.find_one(self._id2_a, preload=True)
        self.assertIsNone(x2['f_11'].value())

    @gen_test
    def test_sub_cls1(self):
        data1 = {'_id': ObjectId, 'f_1': str}
        self.assertDictEqual(TestClass3A.fields, data1)

        data2 = data1.copy()
        data2['f_2'] = int
        self.assertDictEqual(TestClass3B.fields, data2)
        self.assertEqual(TestClass3B.__collection__, TEST_COLLECTION3B)

        data3 = data1.copy()
        data3['f_3'] = float
        self.assertDictEqual(TestClass3C.fields, data3)
        self.assertEqual(TestClass3C.__collection__, TEST_COLLECTION3A)

    @gen_test
    def test_sub_cls2(self):
        xb1 = TestClass3B(f_1=random_str(), f_2=random_int())
        yield xb1.save()
        x4 = TestClass4(x_1=xb1)
        self.assertDictEqual(x4._data.query, {'$set': {'x_1': xb1.dbref}})
        self.assertEqual(x4['x_1.f_1'], xb1['f_1'])

        xb2 = TestClass3B(f_1=random_str(), f_2=random_int())
        yield xb2.save()
        x4 = TestClass4(x_1=xb2.dbref)
        self.assertDictEqual(x4._data.query, {'$set': {'x_1': xb2.dbref}})
        with self.assertRaises(ValueError):
            _ = x4['x_1.f_1']
        yield x4.preload('x_1')
        self.assertEqual(x4['x_1.f_1'], xb2['f_1'])

        xc = TestClass3C(f_1=random_str(), f_3=random_float())
        yield xc.save()
        x4 = TestClass4(x_1=xc)
        self.assertDictEqual(x4._data.query, {'$set': {'x_1': xc.dbref}})
        self.assertEqual(x4['x_1.f_1'], xc['f_1'])

    @gen_test
    def test_ruler_None(self):
        x = yield TestClass2.find_one(self._id2_a)
        self.assertIsNotNone(x['f_11'].value())
        x['f_11'] = None
        self.assertDictEqual(x._data.query, {'$set': {'f_11': None}})

    @gen_test
    def test_ruler_inc(self):
        x = yield TestClass2.find_one(self._id2_a)
        v1 = x['f_2'].value()
        x['f_2'] += 10
        self.assertEqual(x['f_2'].value(), v1 + 10)


# TODO: add test  "res = yield foo.save()"
# TODO: add test  "Documents.remove()"
# TODO: add test  "Documents.filter(...)"
# TODO: add test  "Document.reread(...)"
# TODO: add test  "Documents.reread(...)"
