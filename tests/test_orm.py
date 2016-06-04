# # coding: utf-8
#
# import datetime
#
# from bson import ObjectId
# from tornado.ioloop import IOLoop
# from tornado.testing import AsyncTestCase, gen_test
#
# from mokito.orm import Document, Database
# from test_base import TEST_DB_NAME, TEST_DB_URI
#
# TEST_COLLECTION = 'tst'
#
#
# class TestClass(Document):
#     __uri__ = TEST_DB_URI
#     __database__ = TEST_DB_NAME
#     __collection__ = TEST_COLLECTION
#     fields = {
#         'f_0': None,
#         'f_1': str,
#         'f_2': int,
#         'f_3': bool,
#         'f_4': float,
#         'f_5': datetime.datetime,
#
#         'f_6': {'f_6_1': int, 'f_6_2': str, 'f_6_3': dict, 'f_6_4': {}},
#
#         'f_7': list,
#         'f_8': [str],
#         'f_9': [{'f_9_1': int, 'f_9_2': str, 'f_9_3': dict, }],
#
#         'f_10': (int, str)
#     }
#     required = ['f_1', 'f_2']
#     roles = {'role_1': ['f_0', 'f_1', 'f_5'],
#              'role_2': ['f_6.f_6_1', 'f_7', 'f_10.0']}
#
#
# class ORMTestCase(AsyncTestCase):
#
#     def get_new_ioloop(self):
#         return IOLoop.instance()
#
#     @gen_test
#     def _init_collection(self):
#         data = {
#             '_id': self._id,
#             'f_0': 'foo',
#             'f_1': 100,
#             'f_2': 100,
#             'f_3': True,
#             'f_4': .5,
#             'f_5': self.dt,
#
#             'f_6': {'f_6_1': 200, 'f_6_2': 'string', 'f_6_3': {'a': 1}, 'f_6_4': {'b': 2}},
#
#             'f_7': [1, 'foo', .2],
#             'f_8': ['a', 1, 'c'],
#             'f_9': [
#                 {'f_9_1': 100, 'f_9_2': 's1', 'f_9_3': {'a': 1}},
#                 {'f_9_1': 200, 'f_9_2': 's2', 'f_9_3': {'b': 2}},
#             ],
#
#             'f_10': (200, 'string', 1),
#             'foo': 'bar'
#         }
#         yield Database.get(TEST_DB_NAME)[TEST_COLLECTION].insert(data)
#
#     def setUp(self):
#         super(ORMTestCase, self).setUp()
#         self._id = ObjectId()
#         self.dt = datetime.datetime.now()
#         self._init_collection()
#
#     @gen_test
#     def tearDown(self):
#         # res = yield Database.get(TEST_DB_NAME)[TEST_COLLECTION].find()
#         # print
#         # print 'COL', res
#         yield Database.get(TEST_DB_NAME).command('drop', TEST_COLLECTION)
#         super(ORMTestCase, self).tearDown()
#
#     def test_databases(self):
#         self.assertEqual(Database.all_clients.keys()[0], TEST_DB_NAME)
#
#     @gen_test
#     def test_find_one(self):
#         x = yield TestClass.find_one(self._id)
#         self.assertEqual(x._id, self._id)
#         self.assertEqual(x['f_0'], 'foo')
#         self.assertEqual(x['f_1'], 'bar')
#         self.assertEqual(x['f_2'], 100)
#         self.assertEqual(x['f_3'], True)
#         self.assertEqual(x['f_4'], .5)
#
#         #self.assertEqual(x['f_5'], self.dt)
#
#         print
#         print 'X1', x['f_6']
#         print 'X2', dir(x['f_6'])
#         print 'X1', x['f_6'].inner_data()
#
#
# # 'f_6': {'f_6_1': 200, 'f_6_2': 'string', 'f_6_3': {'a': 1}, 'f_6_4': {'b': 2}},
# #
# # 'f_7': [1, 'foo', .2],
# # 'f_8': ['a', 'b', 'c'],
# # 'f_9': [{'f_9_1': 200, 'f_9_2': 'string', 'f_9_3': {'a': 1}, 'f_9_4': {'b': 2}}],
# #
# # 'f_10': (200, 'string'),
# # 'foo': 'bar'
