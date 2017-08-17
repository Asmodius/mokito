import datetime

from bson import ObjectId, DBRef
import motor.motor_tornado

import mokito

TEST_DB_NAME = 'test_mokito'
TEST_DB_URI = 'mongodb://127.0.0.1:27017'
TEST_COLLECTION1 = 'tst1'
TEST_COLLECTION2 = 'tst2'
TEST_COLLECTION3 = 'tst3'

db = motor.motor_tornado.MotorClient(TEST_DB_URI)[TEST_DB_NAME]


dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
dt3 = datetime.datetime(2016, 3, 4, 5, 6, 7)
dt4 = datetime.datetime(2016, 4, 5, 6, 7, 8)
dt5 = datetime.datetime(2016, 5, 6, 7, 8, 9)
dt6 = datetime.datetime(2016, 6, 7, 8, 9, 10)
dt7 = datetime.datetime(2016, 7, 8, 9, 10, 11)
dt8 = datetime.datetime(2016, 8, 9, 10, 11, 12)
dt9 = datetime.datetime(2016, 9, 10, 11, 12, 13)
dt10 = datetime.datetime(2016, 10, 11, 12, 13, 14)
dt11 = datetime.datetime(2016, 11, 12, 13, 14, 15)
dt12 = datetime.datetime(2016, 12, 13, 14, 15, 16)
xt1 = datetime.datetime(2015, 1, 2, 3, 4, 5)
xt2 = datetime.datetime(2015, 2, 3, 4, 5, 6)
xt3 = datetime.datetime(2015, 3, 4, 5, 6, 7)


col1_id1 = ObjectId()
col1_dbref1 = DBRef(TEST_COLLECTION1, col1_id1)
col1_data1 = {
    '_id': col1_id1,
    'x1': 0.5,
    'x2': [dt1, dt2, dt3],
    'x3': [123, 'z1'],
    'x4': {'a': 1, 'b': 2}
}

col1_id2 = ObjectId()
col1_dbref2 = DBRef(TEST_COLLECTION1, col1_id2)
col1_data2 = {
    '_id': col1_id2,
    'x1': 1.5,
    'x2': [dt4, dt5, dt6],
    'x3': [45601, 'z2'],
    'x4': {'a': 3, 'b': 4},
    'foo': 'bar'
}


col2_id1 = ObjectId()
col2_data1 = {
    '_id': col2_id1,
    'f1': (123, 'foo2'),
    'f2': {'a': 5, 'b': 6},
    'm1': {
        'x1': .1,
        'x2': [dt7, dt8],
        'x3': [7, 'z3'],
        'x4': {'a': 8, 'b': 8}
    },
    'm2': [{
            'x1': .2,
            'x2': [dt9],
            'x3': [8, 'z1'],
            'x4': {'a': 9, 'b': 9}
        }, {
            'x1': .3,
            'x2': [dt10],
            'x3': [9, 'z2'],
            'x4': {'a': 10, 'b': 10}
    }],
    'd1': col1_dbref1,
    'd2': [col1_dbref1, col1_dbref2]
}


col2_id2 = ObjectId()
col2_data2 = {
    '_id': col2_id2,
    'f1': [45602, 'foo3'],
    'f2': {'a': 11, 'b': 12},
    'm1': {
        'x1': .2,
        'x2': [dt11, dt12],
        'x3': [7, 'z3'],
        'x4': {'a': 8, 'b': 8}
    },
    'm2': [{
            'x1': .2,
            'x2': [xt1],
            'x3': [8, 'z1'],
            'x4': {'a': 9, 'b': 9}
        }, {
            'x1': .3,
            'x2': [xt2, xt3],
            'x3': [9, 'z2'],
            'x4': {'a': 10, 'b': 10}
    }],
    'd1': col1_dbref2,
    'd2': [col1_dbref2]
}


col3_id1 = ObjectId()
col3_data1 = {
    '_id': col3_id1,
    'foo': 1,
    'bar': 'zzz'
}

col3_id2 = ObjectId()
col3_data2 = {
    '_id': col3_id2,
    'foo': 2,
    'bar': 'aaa'
}


class Document0(mokito.Document):
    __database__ = db


ch1 = {'z1': 1, 'z2': 2, 'z3': 3}


class Model0(mokito.Model):
    scheme = {
        'x1': float,
        'x2': [datetime.datetime],
        'x3': (int, mokito.Choice(ch1)),
        'x4': {'a': int, 'b': int}
    }


class Model1(Model0):
    @property
    def prop1(self):
        return self['x1'].value + 2


class Document1(Document0):
    __collection__ = TEST_COLLECTION1
    scheme = Model1

    prop1 = Model1.prop1

    @property
    def prop2(self):
        return self._val['x1'].value * 2


class Model2(mokito.Model):
    scheme = {
        'f1': (int, str),
        'f2': {'a': int, 'b': int},
        'm1': Model1,
        'm2': [Model1],
        'd1': Document1,
        'd2': [Document1]
    }


class Document2(Document0):
    __collection__ = TEST_COLLECTION2
    scheme = Model2


class Document3(Document0):
    __collection__ = TEST_COLLECTION3
    scheme = {
        'foo': int,
        'bar': str,
    }


class Document4(Document3):
    sorting = ['-foo']

# TODO: add test update_values
