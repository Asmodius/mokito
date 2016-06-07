# coding: utf-8

import sys
import random
import string
import datetime

from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, gen_test

import mokito


TEST_DB_NAME = 'test_mokito'
TEST_DB_URI = "mongodb://127.0.0.1:27017"


def random_int():
    return random.randint(-sys.maxint, sys.maxint)


def random_float():
    return random.uniform(-sys.maxint, sys.maxint)


def random_str(n=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))


def random_datetime():
    return datetime.datetime(random.randint(2000, 2100),
                             random.randint(1, 12),
                             random.randint(1, 28),
                             random.randint(0, 23),
                             random.randint(0, 59),
                             random.randint(0, 59))


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
