# coding: utf-8

from bson import ObjectId
from tornado.testing import gen_test
from pymongo import ASCENDING

from tests.util import BaseTestCase
import mokito


class CursorTestCase(BaseTestCase):

    def test_collection_name(self):
        cur = self.db.foo
        self.assertEqual(cur.collection_name, 'foo')

    def test_full_collection_name(self):
        def cn(name=None):
            return '%s.%s' % (self.db_name, name or 'foo')

        cur = self.db.foo
        self.assertEqual(cur.full_collection_name, cn())
        self.assertEqual(cur._full_collection_name('$cmd'), cn('$cmd'))

    @gen_test
    def test_insert_1(self):
        res = yield self.db.foo.insert({'foo': 1})
        self.assertIsInstance(res, ObjectId)

    @gen_test
    def test_insert_2(self):
        res = yield self.db.foo.insert([{'bar': 1}, {'bar': 2}])
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], ObjectId)
        self.assertIsInstance(res[1], ObjectId)

    @gen_test
    def test_insert_3(self):
        _id = ObjectId()
        res = yield self.db.foo.insert({'foo': 3, '_id': _id})
        self.assertEqual(_id, res)

    @gen_test
    def test_insert_4(self):
        _id = ObjectId()
        data = {'_id': _id, 'foo': 1}
        res = yield self.db.foo.insert(data, False)
        self.assertEqual(_id, res)

        res = yield self.db.foo.find_one()
        self.assertDictEqual(data, res)

    @gen_test
    def test_insert_wrong(self):
        _id = ObjectId()
        data = {'foo': 1, '_id': _id}
        yield self.db.foo.insert(data)
        with self.assertRaises(mokito.errors.MokitoResponseError):
            yield self.db.foo.insert(data)

    @gen_test
    def test_count_1(self):
        res = yield self.db.foo.count()
        self.assertFalse(res)

    @gen_test
    def test_count_2(self):
        yield self.db.foo.insert([{'bar': 1}, {'bar': 2}])
        res = yield self.db.foo.count()
        self.assertEqual(res, 2)

        res = yield self.db.foo.count({'bar': 1})
        self.assertEqual(res, 1)

    @gen_test
    def test_remove_1(self):
        _id1 = ObjectId()
        data = [{'bar': 1, '_id': _id1}, {'bar': 2}, {'bar': 3}]

        yield self.db.foo.insert(data)
        res = yield self.db.foo.remove()
        self.assertEqual(res, 3)
        res = yield self.db.foo.count()
        self.assertFalse(res)

        yield self.db.foo.insert(data)
        res = yield self.db.foo.remove(_id1)
        self.assertEqual(res, 1)
        res = yield self.db.foo.count()
        self.assertEqual(res, 2)

    @gen_test
    def test_remove_2(self):
        _id1 = ObjectId()
        _id2 = ObjectId()

        yield self.db.foo.insert([{'bar': 1, '_id': _id1}, {'bar': 2}])
        res = yield self.db.foo.remove(_id2)
        self.assertEqual(res, 0)
        res = yield self.db.foo.count()
        self.assertEqual(res, 2)

    @gen_test
    def test_remove_3(self):
        yield self.db.foo.insert([{'bar': 1}, {'bar': 1}, {'bar': 2}])
        res = yield self.db.foo.remove({'bar': 1})
        self.assertEqual(res, 2)
        res = yield self.db.foo.count()
        self.assertEqual(res, 1)

    @gen_test
    def test_find_one(self):
        res = yield self.db.foo.find_one()
        self.assertIsNone(res)

        _id1 = ObjectId()
        data1 = {'_id': _id1, 'bar': 1, 'foo': 'foo'}
        _id2 = ObjectId()
        data2 = {'_id': _id2, 'bar': 2, 'foo': 'foo'}
        yield self.db.foo.insert([data1, data2])

        res = yield self.db.foo.find_one(_id1)
        self.assertDictEqual(data1, res)

        res = yield self.db.foo.find_one({'bar': 2})
        self.assertDictEqual(data2, res)

        res = yield self.db.foo.find_one({'bar': 3})
        self.assertIsNone(res)

        res = yield self.db.foo.find_one(_id1, {'bar': 1, 'foo': 1})
        self.assertDictEqual(data1, res)

        res = yield self.db.foo.find_one(_id1, {'bar': 1})
        self.assertDictEqual({'_id': _id1, 'bar': 1}, res)

        res = yield self.db.foo.find_one(_id2, ['foo'])
        self.assertDictEqual({'_id': _id2, 'foo': 'foo'}, res)

    @gen_test
    def test_find_1(self):
        res = yield self.db.foo.find()
        self.assertIsInstance(res, list)
        self.assertFalse(res)

        _id1 = ObjectId()
        data1 = {'_id': _id1, 'bar': 1, 'foo': 'foo'}
        _id2 = ObjectId()
        data2 = {'_id': _id2, 'bar': 2, 'foo': 'foo'}
        yield self.db.foo.insert([data1, data2])

        res = yield self.db.foo.find()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)

        res = yield self.db.foo.find({'_id': _id1})
        self.assertDictEqual(data1, res[0])

        res = yield self.db.foo.find({'bar': 2})
        self.assertDictEqual(data2, res[0])

        res = yield self.db.foo.find({'foo': 'foo'}, ['bar'], limit=1)
        self.assertDictEqual({'_id': _id1, 'bar': 1}, res[0])

        res = yield self.db.foo.find({'foo': 'foo'}, ['bar'], skip=1)
        self.assertDictEqual({'_id': _id2, 'bar': 2}, res[0])

    @gen_test
    def test_find_2(self):
        _id1 = ObjectId()
        data1 = {'_id': _id1, 'bar': 1, 'foo': 'foo'}
        _id2 = ObjectId()
        data2 = {'_id': _id2, 'bar': 2, 'foo': 'foo'}
        yield self.db.foo.insert([data1, data2])

        res = yield self.db.foo.find(sort=[('bar', ASCENDING)])
        self.assertDictEqual(data1, res[0])
        self.assertDictEqual(data2, res[1])

        res = yield self.db.foo.find(sort='-bar')
        self.assertDictEqual(data2, res[0])
        self.assertDictEqual(data1, res[1])

    @gen_test
    def test_update_1(self):
        _id1 = ObjectId()
        data1 = {'_id': _id1, 'bar': 1, 'foo': 'foo'}
        _id2 = ObjectId()
        data2 = {'_id': _id2, 'bar': 2, 'foo': 'foo'}
        yield self.db.foo.insert([data1, data2])

        res = yield self.db.foo.update({'_id': _id1}, {'foo': 'baz'}, no_replace=True)
        self.assertTrue(res)
        res = yield self.db.foo.find()
        self.assertDictEqual({'_id': _id1, 'bar': 1, 'foo': 'baz'}, res[0])
        self.assertDictEqual(data2, res[1])

        res = yield self.db.foo.update({'_id': _id2}, {'foo': 'baz'})
        self.assertTrue(res)
        res = yield self.db.foo.find()
        self.assertDictEqual({'_id': _id1, 'bar': 1, 'foo': 'baz'}, res[0])
        self.assertDictEqual({'_id': _id2, 'foo': 'baz'}, res[1])

    @gen_test
    def test_update_2(self):
        _id1 = ObjectId()
        data1 = {'_id': _id1, 'bar': 1, 'foo': 'foo'}
        _id2 = ObjectId()
        data2 = {'_id': _id2, 'bar': 2, 'foo': 'foo'}
        yield self.db.foo.insert([data1, data2])

        res = yield self.db.foo.update({'foo': 'foo'}, {"$set": {'bar': 3}})
        self.assertTrue(res)
        res = yield self.db.foo.find()
        self.assertDictEqual({'_id': _id1, 'bar': 3, 'foo': 'foo'}, res[0])
        self.assertDictEqual(data2, res[1])

        res = yield self.db.foo.update({'foo': 'foo'}, {"$set": {'bar': 4}}, multi=True)
        self.assertTrue(res)
        res = yield self.db.foo.find()
        self.assertDictEqual({'_id': _id1, 'bar': 4, 'foo': 'foo'}, res[0])
        self.assertDictEqual({'_id': _id2, 'bar': 4, 'foo': 'foo'}, res[1])

    @gen_test
    def test_update_3(self):
        _id1 = ObjectId()
        data1 = {'_id': _id1, 'bar': 1, 'foo': 'foo'}
        _id2 = ObjectId()
        data2 = {'_id': _id2, 'bar': 2, 'foo': 'foo'}
        yield self.db.foo.insert(data1)

        res = yield self.db.foo.update({'_id': _id2}, data2)
        self.assertFalse(res)
        res = yield self.db.foo.find_one(_id2)
        self.assertIsNone(res)

        res = yield self.db.foo.update({'_id': _id2}, data2, upsert=True)
        self.assertEqual(_id2, res)
        res = yield self.db.foo.find_one(_id2)
        self.assertDictEqual(data2, res)

    @gen_test
    def test_distinct_1(self):
        _id1 = ObjectId()
        data1 = {'_id': _id1, 'bar': 1, 'foo': 'foo'}
        _id2 = ObjectId()
        data2 = {'_id': _id2, 'bar': 2, 'foo': 'foo'}
        yield self.db.foo.insert([data1, data2])

        res = yield self.db.foo.distinct('bar')
        self.assertListEqual(res, [1, 2])

    @gen_test
    def test_distinct_2(self):
        _id1 = ObjectId()
        data1 = {'_id': _id1, 'bar': 1, 'foo': 'foo'}
        _id2 = ObjectId()
        data2 = {'_id': _id2, 'bar': 2, 'foo': 'bar'}
        yield self.db.foo.insert([data1, data2])

        res = yield self.db.foo.distinct('bar', {'foo': 'bar'})
        self.assertListEqual(res, [2])
