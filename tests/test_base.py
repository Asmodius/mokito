# coding: utf-8

from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, gen_test

import mokito

TEST_DB_NAME = 'test_mokito'
TEST_DB_URI = "mongodb://127.0.0.1:27017"


class BaseTestCase(AsyncTestCase):

    def get_new_ioloop(self):
        return IOLoop.instance()

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.db_name = TEST_DB_NAME
        self.db = mokito.Client(TEST_DB_NAME, TEST_DB_URI)

    @gen_test
    def tearDown(self):
        yield self.db.command('dropDatabase')
        super(BaseTestCase, self).tearDown()
