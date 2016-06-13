# coding: utf-8

import copy
import datetime

from bson import ObjectId
from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, gen_test

from mokito.orm import Document, Database
from tests.util import (
    TEST_DB_NAME,
    TEST_DB_URI,
    random_int,
    random_datetime,
    random_float,
    random_str
)

TEST_COLLECTION = 'tst'


class TestClass(Document):
    __uri__ = TEST_DB_URI
    __database__ = TEST_DB_NAME
    __collection__ = TEST_COLLECTION
    fields = {
        'f_0': None,
        'f_1': str,
        'f_2': int,
        'f_3': bool,
        'f_4': float,
        'f_5': datetime.datetime,
        'f_6': {'f_6_1': int, 'f_6_2': str, 'f_6_3': {}},
        'f_7': list,
        'f_8': [str],
        'f_9': [{'f_9_1': int, 'f_9_2': str, 'f_9_3': dict}],
        'f_10': (int, str)
    }
    roles = {'role_1': ['f_0', 'f_5', 'prop'],
             'role_2': ['f_6.f_6_1', 'f_7', 'f_10.0']}

    @property
    def prop(self):
        return '%s:%s' % (self['f_1'], self['f_2'])

    def to_json(self, *role, **kwargs):
        ret = super(TestClass, self).to_json(*role, **kwargs)
        if 'f_5' in ret:
            ret['f_5'] = ret['f_5'].strftime("%B %d, %Y")
        return ret


class ORMTestCase(AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super(ORMTestCase, self).__init__(*args, **kwargs)

        self._id1 = ObjectId()
        self.data1 = {
            '_id': self._id1,
            'f_0': random_str(),
            'f_1': random_str(),
            'f_2': random_int(),
            'f_3': True,
            'f_4': random_float(),
            'f_5': random_datetime(),
            'f_6': {
                'f_6_1': random_int(),
                'f_6_2': random_str(),
                'f_6_3': {'a': random_int()}
            },
            'f_7': [random_int(), random_str(), random_float()],
            'f_8': [random_str()],
            'f_9': [{'f_9_1': random_int(), 'f_9_2': random_str(), 'f_9_3': {'a': random_int()}},
                    {'f_9_1': random_int(), 'f_9_2': random_str(), 'f_9_3': {'b': random_int()}}],
            'f_10': [random_int(), random_str()],
            'foo': 'bar'
        }

        self._id2 = ObjectId()
        self.data2 = {
            '_id': self._id2,
            'f_0': random_str(),
            'f_1': random_str(),
            'f_2': random_int(),
            'f_3': False,
            'f_4': random_float(),
            'f_5': random_datetime(),
            'f_6': {
                'f_6_1': random_int(),
                'f_6_2': random_str(),
                'f_6_3': {'a': random_int()}
            },
            'f_7': [random_int(), random_str(), random_float()],
            'f_8': ['f_8'],
            'f_9': [{'f_9_1': random_int(), 'f_9_2': random_str(), 'f_9_3': {'a': random_int()}},
                    {'f_9_1': random_int(), 'f_9_2': random_str(), 'f_9_3': {'b': random_int()}}],
            'f_10': [random_int(), random_str()],
            'foo': 'baz'
        }

    def get_new_ioloop(self):
        return IOLoop.instance()

    @gen_test
    def _init_collection(self):
        self.db = Database.get(TEST_DB_NAME)
        yield self.db[TEST_COLLECTION].insert([self.data1, self.data2])

    def setUp(self):
        super(ORMTestCase, self).setUp()
        self._init_collection()

    @gen_test
    def tearDown(self):
        yield self.db.command('drop', TEST_COLLECTION)
        super(ORMTestCase, self).tearDown()

    def _check_data(self, obj, data):
        for i in ('f_0', 'f_1', 'f_2', 'f_3', 'f_4', 'f_5'):
            self.assertEqual(obj[i].value(), data[i])

        self.assertDictEqual(obj['f_6'].value(), data['f_6'])
        self.assertEqual(obj['f_7'].value(), data['f_7'])
        self.assertEqual(obj['f_8'].value(), data['f_8'])
        self.assertDictEqual(obj['f_9'][0].value(), data['f_9'][0])
        self.assertDictEqual(obj['f_9'][1].value(), data['f_9'][1])
        self.assertEqual(obj['f_10'].value(), data['f_10'])
        self.assertIsNone(obj['foo'])

    def test_databases(self):
        self.assertEqual(Database.all_clients.keys()[0], TEST_DB_NAME)

    @gen_test
    def test_find_one(self):
        for _id, data in [(self._id1, self.data1), (self._id2, self.data2)]:
            x = yield TestClass.find_one(_id)
            self.assertEqual(x.pk, _id)
            self._check_data(x, data)

    @gen_test
    def test_find(self):
        for x in (yield TestClass.find()):
            data = self.data1 if x.pk == self._id1 else self.data2
            self._check_data(x, data)

    @gen_test
    def test_count(self):
        self.assertEqual((yield TestClass.count()), 2)

    @gen_test
    def test_save_1(self):
        n = random_datetime()
        x = yield TestClass.find_one(self._id1)
        self.assertFalse(x.dirty)
        x['f_0'] = n
        self.assertTrue(x.dirty)
        yield x.save()
        self.assertFalse(x.dirty)

        data = yield self.db[TEST_COLLECTION].find_one(self._id1)
        self.assertEqual(data['f_0'], n)
        self.assertEqual(x['f_0'].value(), n)

        data = yield self.db[TEST_COLLECTION].count()
        self.assertEqual(data, 2)

    @gen_test
    def test_save_2(self):
        data = copy.copy(self.data1)
        del data['_id']

        x = TestClass(data)
        self.assertIsNone(x.pk)
        self.assertTrue(x.dirty)
        self._check_data(x, data)

        yield x.save()
        self.assertIsNotNone(x.pk)
        self.assertFalse(x.dirty)
        self._check_data(x, data)

        data = yield self.db[TEST_COLLECTION].find_one(x.pk)
        self._check_data(x, data)

        data = yield self.db[TEST_COLLECTION].count()
        self.assertEqual(data, 3)

    @gen_test
    def test_to_prop(self):
        x = yield TestClass.find_one(self._id1)
        self.assertEqual(x.prop, '%s:%s' % (self.data1['f_1'], self.data1['f_2']))

    @gen_test
    def test_to_json_1(self):
        x = yield TestClass.find_one(self._id1)
        data1 = x.to_json()
        data2 = copy.copy(self.data1)
        data2['f_5'] = data2['f_5'].strftime("%B %d, %Y")
        data2['_id'] = str(data2['_id'])
        del data2['foo']
        self.assertDictEqual(data1, data2)

    @gen_test
    def test_to_json_2(self):
        x = yield TestClass.find_one(self._id1)

        data1 = x.to_json('role_1', no_id=True)
        data2 = {
            'f_0': self.data1['f_0'],
            'f_5': self.data1['f_5'].strftime("%B %d, %Y"),
            'prop': '%s:%s' % (self.data1['f_1'], self.data1['f_2'])
        }
        self.assertDictEqual(data1, data2)

        data1 = x.to_json('role_1')
        data2['_id'] = str(self._id1)
        self.assertDictEqual(data1, data2)

    @gen_test
    def test_to_json_3(self):
        x = yield TestClass.find_one(self._id1)

        data1 = x.to_json('role_2', no_id=True)
        data2 = {
            'f_7': self.data1['f_7'],
            'f_10.0': self.data1['f_10'][0],
            'f_6.f_6_1': self.data1['f_6']['f_6_1']
        }
        self.assertDictEqual(data1, data2)

        data1 = x.to_json('role_2')
        data2['_id'] = str(self._id1)
        self.assertDictEqual(data1, data2)

    @gen_test
    def test_from_json_1(self):
        data = copy.copy(self.data1)
        x = yield TestClass.from_json(data)
        self.assertFalse(x.dirty)

    @gen_test
    def test_from_json_2(self):
        data = copy.copy(self.data1)
        data['f_0'] = 'foo'
        x = yield TestClass.from_json(data)
        self.assertTrue(x.dirty)
        self.assertDictEqual(x._data.query(), {'$set': {'f_0': 'foo'}})

    @gen_test
    def test_distinct(self):
        x = yield TestClass.distinct('f_0')
        self.assertListEqual(x, [self.data1['f_0'], self.data2['f_0']])

        x = yield TestClass.distinct('f_0', {'f_1': self.data1['f_1']})
        self.assertListEqual(x, [self.data1['f_0']])
