# coding: utf-8

import unittest

from tornado.testing import gen_test

import mokito
from tests.util import BaseTestCase


# TODO: add test connection pool

class ConnectionTestCase(BaseTestCase):

    def test_db_name(self):
        self.assertEqual(self.db._db_name, self.db_name)

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
        for i in col:
            yield self.db[i].insert({'foo': 1})
        res = yield self.db.collection_names()
        self.assertListEqual(col, res)

    def test_get_cursor(self):
        res = self.db.get_cursor('foo')
        self.assertIsInstance(res, mokito.cursor.Cursor)

