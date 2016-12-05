# coding: utf-8

import datetime

from bson import ObjectId, DBRef
# from tornado.gen import coroutine, Return

import mokito


TEST_DB_NAME = 'test_mokito'
TEST_DB_URI = "mongodb://127.0.0.1:27017"
TEST_COLLECTION1 = 'tst1'
TEST_COLLECTION2 = 'tst2'

col1_id1 = ObjectId()
col1_dbref1 = DBRef('TEST_COLLECTION1', col1_id1)
col1_data1 = {
    '_id': col1_id1,
    'x1': 0.5,
    'x2': [datetime.datetime(2016, 1, 2, 3, 4, 5),
           datetime.datetime(2016, 2, 3, 4, 5, 6),
           datetime.datetime(2016, 3, 4, 5, 6, 7)],
    'x3': [123, 'foo'],
    'x4': {'a': 1, 'b': 2}
}

col1_id2 = ObjectId()
col1_dbref2 = DBRef('TEST_COLLECTION1', col1_id2)
col1_data2 = {
    '_id': col1_id2,
    'x1': 1.5,
    'x2': [datetime.datetime(2016, 4, 5, 6, 7, 8),
           datetime.datetime(2016, 5, 6, 7, 8, 9),
           datetime.datetime(2016, 6, 7, 8, 9, 10)],
    'x3': [45601, 'bar'],
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
        'x2': [datetime.datetime(2016, 7, 8, 9, 10, 11),
               datetime.datetime(2016, 8, 9, 10, 11, 12)],
        'x3': [7, 'x'],
        'x4': {'a': 8, 'b': 8}
    },
    'm2': [{
            'x1': .2,
            'x2': [datetime.datetime(2016, 9, 10, 11, 12, 13)],
            'x3': [8, 'y'],
            'x4': {'a': 9, 'b': 9}
        }, {
            'x1': .3,
            'x2': [datetime.datetime(2016, 10, 11, 12, 13, 14)],
            'x3': [9, 'z'],
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
        'x2': [datetime.datetime(2016, 11, 12, 13, 14, 15),
               datetime.datetime(2016, 12, 13, 14, 15, 16)],
        'x3': [7, 'x'],
        'x4': {'a': 8, 'b': 8}
    },
    'm2': [{
            'x1': .2,
            'x2': [datetime.datetime(2015, 1, 2, 3, 4, 5)],
            'x3': [8, 'y'],
            'x4': {'a': 9, 'b': 9}
        }, {
            'x1': .3,
            'x2': [datetime.datetime(2015, 2, 3, 4, 5, 6),
                   datetime.datetime(2015, 3, 4, 5, 6, 7)],
            'x3': [9, 'z'],
            'x4': {'a': 10, 'b': 10}
    }],
    'd1': col1_dbref2,
    'd2': [col1_dbref2]
}


class Document0(mokito.Document):
    __uri__ = TEST_DB_URI
    __database__ = TEST_DB_NAME


class Model0(mokito.Model):
    fields = {
        'x1': float,
        'x2': [datetime.datetime],
        'x3': (int, str),
        'x4': {'a': int, 'b': int}
    }
    # roles = {
    #     'r1': ['_id', 'x1', 'x2', 'x3'],
    #     'r2': ['x2', 'x3', 'x4'],
    #     'r3': ['prop1', 'prop2'],
    #     'r4': ['a1', 'a2', 'a3'],
    #     'r5': ['x3.1', 'x4.a', 'x4.b'],
    # }
    aliases = {'a1': 'x1', 'a2': 'prop1', 'a3': 'prop2'}


# 'r6': [['x2.0', {'_format': '%d/%m/%y'}], ['x2.1', {'tz_name': 'Asia/Novosibirsk'}], 'x3.2']

class Model1(Model0):
    @property
    def prop1(self):
        return self['x1'].value + 2


class Document1(Document0):
    __collection__ = TEST_COLLECTION1
    __model__ = Model1

    @property
    def prop2(self):
        return self._data['x1'].value * 2


class Model2(mokito.Model):
    fields = {
        'f1': (int, str),
        'f2': {'a': int, 'b': int},
        'm1': Model0,
        'm2': [Model0],
        'd1': Document1,
        'd2': [Document1]
    }


class Document2(Document0):
    __collection__ = TEST_COLLECTION2
    __model__ = Model2
