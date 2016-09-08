# coding: utf-8

import sys
import random
import string
import datetime

from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, gen_test
from tornado.gen import coroutine, Return

import mokito


TEST_DB_NAME = 'test_mokito'
TEST_DB_URI = "mongodb://127.0.0.1:27017"
TEST_COLLECTION1 = 'tst1'
TEST_COLLECTION2 = 'tst2'
TEST_COLLECTION3A = 'tst3a'
TEST_COLLECTION3B = 'tst3b'
TEST_COLLECTION4 = 'tst4'
TEST_COLLECTION5 = 'tst5'


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


class TestClass1(mokito.orm.Document):
    __uri__ = TEST_DB_URI
    __database__ = TEST_DB_NAME
    __collection__ = TEST_COLLECTION1
    fields = {
        'f_0': None,
        'f_1': str,
    }

    @property
    def prop(self):
        return '%s:%s' % (self['f_1'], self['f_0'])

    roles = {'role_1': ['f_0']}

data1_a = {
    'f_0': random_int(),
    'f_1': random_str()
}

data1_b = {
    'f_0': random_int(),
    'f_1': random_str()
}


class TestClass2(mokito.orm.Document):
    __uri__ = TEST_DB_URI
    __database__ = TEST_DB_NAME
    __collection__ = TEST_COLLECTION2
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
        'f_10': (int, str),

        'f_11': TestClass1,
        'f_12': [TestClass1],
        'f_13': (int, TestClass1)
    }
    roles = {'role_1': ['f_0', 'f_5', 'prop'],
             'role_2': ['f_6.f_6_1', 'f_7', 'f_10.0'],
             'role_3': ['f_11'],
             'role_4': ['f_12.0', 'f_13.1.f_0']}

    @property
    def prop(self):
        return '%s:%s' % (self['f_1'], self['f_2'])

    @coroutine
    def to_json(self, *role):
        ret = yield super(TestClass2, self).to_json(*role)
        if 'f_5' in ret:
            ret['f_5'] = ret['f_5'].strftime("%B %d, %Y")
        raise Return(ret)


data2_a = {
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
    'f_9': [
        {
            'f_9_1': random_int(),
            'f_9_2': random_str(),
            'f_9_3': {'a': random_int()}
        }, {
            'f_9_1': random_int(),
            'f_9_2': random_str(),
            'f_9_3': {'b': random_int()}
        }
    ],
    'f_10': [random_int(), random_str()],
    'foo': 'bar'
}

data2_b = {
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


class TestClass3A(mokito.orm.Document):
    __uri__ = TEST_DB_URI
    __database__ = TEST_DB_NAME
    __collection__ = TEST_COLLECTION3A
    fields = {
        'f_1': str,
    }


class TestClass3B(TestClass3A):
    __collection__ = TEST_COLLECTION3B
    fields = {
        'f_2': int,
    }


class TestClass3C(TestClass3A):
    fields = {
        'f_3': float,
    }


class TestClass3D(mokito.orm.Document):
    __uri__ = TEST_DB_URI
    __database__ = TEST_DB_NAME
    __collection__ = TEST_COLLECTION5
    fields = {
        'f_3': float,
    }


class TestClass4(mokito.orm.Document):
    __uri__ = TEST_DB_URI
    __database__ = TEST_DB_NAME
    __collection__ = TEST_COLLECTION4
    fields = {
        'x_1': TestClass3A
    }
