# coding: utf-8

from tornado.ioloop import IOLoop
from tornado.gen import coroutine

import mokito

TEST_DB_NAME = 'test_mokito'
TEST_DB_URI = "mongodb://127.0.0.1:27017"
TEST_COLLECTION3 = 'tst3'


class TestClass3A(mokito.orm.Document):
    __uri__ = TEST_DB_URI
    __database__ = TEST_DB_NAME
    __collection__ = TEST_COLLECTION3
    fields = {
        'f_0': None,
        'f_1': str,
    }

    def info(self):
        return '%s: %s' % (self.__class__.__name__, self.fields)


class TestClass3B(TestClass3A):
    fields = {
        'f_3': int,
    }


@coroutine
def main():
    print
    print 'ASYNC1', mokito.KnownClasses.data
    print 'ASYNC2', TestClass3B.fields

IOLoop.current().run_sync(main)
