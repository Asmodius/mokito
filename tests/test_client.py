# coding: utf-8

import unittest

from tornado.testing import gen_test, AsyncTestCase
from tornado.ioloop import IOLoop

import mokito
from tests.util import TEST_DB_NAME, TEST_DB_URI


# TODO: add test connection pool

class ConnectionTestCase(AsyncTestCase):

    def get_new_ioloop(self):
        return IOLoop.instance()

    def setUp(self):
        super(ConnectionTestCase, self).setUp()
        self.db = mokito.Client(TEST_DB_NAME, TEST_DB_URI)

    @gen_test
    def tearDown(self):
        yield self.db.command('dropDatabase')
        super(ConnectionTestCase, self).tearDown()

    def test_db_name(self):
        self.assertEqual(self.db._db_name, TEST_DB_NAME)

    @gen_test
    def test_command_1(self):
        res = yield self.db.command('buildinfo')
        self.assertIsNotNone(res)
        self.assertTrue(bool(res['ok']))

    @gen_test
    def test_command_2(self):
        yield self.db.foo.insert({'foo': 'bar'})

        res = yield self.db.foo.find_one()
        self.assertIsNotNone(res)

        res = yield self.db.command('drop', 'foo')
        self.assertIsNotNone(res)
        self.assertTrue(bool(res['ok']))

        res = yield self.db.foo.find_one()
        self.assertIsNone(res)

    @unittest.skip('not implemented method "close"')
    def test_close(self):
        self.db.close()

    @gen_test
    def test_uri_wrong(self):
        db = mokito.Client('wrong', "mongodb://127.0.0.1:27017aaa")
        with self.assertRaises(mokito.errors.MokitoInvalidURIError):
            yield db.command('buildinfo')

    @gen_test
    def test_collection_names(self):
        col = [u'foo', u'bar']
        for i in col+[u'tst1', u'tst2']:
            yield self.db.command('drop', i)

        for i in col:
            yield self.db[i].insert({'foo': 1})

        res = yield self.db.collection_names()
        self.assertListEqual(res, col)

        yield self.db.command('drop', 'bar')
        res = yield self.db.collection_names()
        self.assertListEqual(res, [u'foo'])

        yield self.db.command('drop', 'foo')
        res = yield self.db.collection_names()
        self.assertListEqual(res, [])
