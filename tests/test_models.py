# # coding: utf-8
#
# import unittest
# import datetime
#
# import mokito
#
#
# class TestModels(unittest.TestCase):
#     def test_model_get_1(self):
#         class Model0(mokito.Model):
#             fields = {
#                 'd1': int,
#                 'd2': [str],
#                 'd3': (int, str),
#                 'd4': {
#                     'dd1': int,
#                     'dd2': [str],
#                     'dd3': (int, str)
#                 }
#             }
#
#         f = Model0()
#
#         self.assertEqual(f['d1'].get(), None)
#         self.assertEqual(f['d1'].value, None)
#         self.assertEqual(f['d2'].get(), [])
#         self.assertEqual(f['d2'].value, [])
#         self.assertEqual(f['d3'].get(), [None, None])
#         self.assertEqual(f['d3'].value, [None, None])
#         self.assertDictEqual(f['d4'].get(), {'dd1': None, 'dd2': [], 'dd3': [None, None]})
#         self.assertDictEqual(f['d4'].value, {'dd1': None, 'dd2': [], 'dd3': [None, None]})
#         self.assertEqual(f['d4.dd1'].get(), None)
#         self.assertEqual(f['d4.dd1'].value, None)
#         self.assertEqual(f['d4']['dd1'].get(), None)
#         self.assertEqual(f['d4']['dd1'].value, None)
#         self.assertEqual(f['d4.dd2'].get(), [])
#         self.assertEqual(f['d4.dd2'].value, [])
#         self.assertEqual(f['d4']['dd2'].get(), [])
#         self.assertEqual(f['d4']['dd2'].value, [])
#         self.assertEqual(f['d4.dd3'].get(), [None, None])
#         self.assertEqual(f['d4.dd3'].value, [None, None])
#         self.assertEqual(f['d4']['dd3'].get(), [None, None])
#         self.assertEqual(f['d4']['dd3'].value, [None, None])
#
#     def test_model_get_2(self):
#         class SubModel0(mokito.Model):
#             fields = {
#                 'd1': int,
#                 'd2': [str],
#                 'd3': (int, str),
#                 'd4': {
#                     'dd1': int,
#                     'dd2': [str],
#                     'dd3': (int, str)
#                 }
#             }
#
#         class SubModel1(mokito.Model):
#             fields = {
#                 'x': int
#             }
#
#         class Model0(mokito.Model):
#             fields = {
#                 'm1': SubModel0,
#                 'm2': SubModel1
#             }
#
#         f = Model0()
#
#         self.assertEqual(f['m1.d1'].get(), None)
#         self.assertEqual(f['m1.d1'].value, None)
#         self.assertEqual(f['m1.d2'].get(), [])
#         self.assertEqual(f['m1.d2'].value, [])
#         self.assertEqual(f['m1.d3'].get(), [None, None])
#         self.assertEqual(f['m1.d3'].value, [None, None])
#         self.assertDictEqual(f['m1.d4'].get(), {'dd1': None, 'dd2': [], 'dd3': [None, None]})
#         self.assertDictEqual(f['m1.d4'].value, {'dd1': None, 'dd2': [], 'dd3': [None, None]})
#         self.assertEqual(f['m1.d4.dd1'].get(), None)
#         self.assertEqual(f['m1.d4.dd1'].value, None)
#         self.assertEqual(f['m1.d4']['dd1'].get(), None)
#         self.assertEqual(f['m1.d4']['dd1'].value, None)
#         self.assertEqual(f['m1.d4.dd2'].get(), [])
#         self.assertEqual(f['m1.d4.dd2'].value, [])
#         self.assertEqual(f['m1.d4']['dd2'].get(), [])
#         self.assertEqual(f['m1.d4']['dd2'].value, [])
#         self.assertEqual(f['m1.d4.dd3'].get(), [None, None])
#         self.assertEqual(f['m1.d4.dd3'].value, [None, None])
#         self.assertEqual(f['m1.d4']['dd3'].get(), [None, None])
#         self.assertEqual(f['m1.d4']['dd3'].value, [None, None])
#
#         self.assertEqual(f['m2']['x'].get(), None)
#
#     def test_model_set_1(self):
#         class Model0(mokito.Model):
#             fields = {
#                 'd1': int,
#                 'd2': [str],
#                 'd3': (int, str),
#                 'd4': {
#                     'dd1': int,
#                     'dd2': [str],
#                     'dd3': (int, str)
#                 }
#             }
#
#         f = Model0()
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': None,
#             'd2': [],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d1'] = 123
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': [],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d2.0'] = 123
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['123'],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d2'][1] = 'foo'
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['123', 'foo'],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d2'].append('bar')
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['123', 'foo', 'bar'],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d2'].set(['z', 123])
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, None],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d3.0'] = 123
#         f['d3.1'] = 123
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [123, '123'],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d3'] = [None, 'foo']
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd1'] = 456
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd2'].append('bar')
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': ['bar'],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd2.2'] = 'x'
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': ['bar', None, 'x'],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd3.1'] = 456
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': ['bar', None, 'x'],
#                 'dd3': [None, '456']
#             }
#         })
#
#         f.set({
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         })
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         })
#
#     def test_model_set_2(self):
#         class SubModel0(mokito.Model):
#                 fields = {
#                     'd1': int,
#                     'd2': [str],
#                     'd4': {
#                         'dd3': (int, str)
#                     }
#                 }
#
#         class SubModel1(mokito.Model):
#             fields = {
#                 'x': int
#             }
#
#         class Model0(mokito.Model):
#             fields = {
#                 'm1': SubModel0,
#                 'm2': SubModel1
#             }
#
#         f = Model0()
#
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'm1': {
#                 'd1': None,
#                 'd2': [],
#                 'd4': {
#                     'dd3': [None, None]
#                 }
#             },
#             'm2': {
#                 'x': None
#             }
#         })
#
#         f['m1']['d1'] = 123
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'm1': {
#                 'd1': 123,
#                 'd2': [],
#                 'd4': {
#                     'dd3': [None, None]
#                 }
#             },
#             'm2': {
#                 'x': None
#             }
#         })
#
#         f['m1.d2.0'] = 123
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'm1': {
#                 'd1': 123,
#                 'd2': ['123'],
#                 'd4': {
#                     'dd3': [None, None]
#                 }
#             },
#             'm2': {
#                 'x': None
#             }
#         })
#
#         f['m1']['d2'][1] = 'foo'
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'm1': {
#                 'd1': 123,
#                 'd2': ['123', 'foo'],
#                 'd4': {
#                     'dd3': [None, None]
#                 }
#             },
#             'm2': {
#                 'x': None
#             }
#         })
#
#         f['m2'].set({'x': 456})
#
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'm1': {
#                 'd1': 123,
#                 'd2': ['123', 'foo'],
#                 'd4': {
#                     'dd3': [None, None]
#                 }
#             },
#             'm2': {
#                 'x': 456
#             }
#         })
#
#         f['m1.d4.dd3.1'] = 'x'
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'm1': {
#                 'd1': 123,
#                 'd2': ['123', 'foo'],
#                 'd4': {
#                     'dd3': [None, 'x']
#                 }
#             },
#             'm2': {
#                 'x': 456
#             }
#         })
#
#         f.set({
#             'm1': {
#                 'd1': 456,
#                 'd2': ['foo', 'bar'],
#                 'd4': {
#                     'dd3': [123, 'x']
#                 }
#             },
#             'm2': {
#                 'x': 123
#             }
#         })
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'm1': {
#                 'd1': 456,
#                 'd2': ['foo', 'bar'],
#                 'd4': {
#                     'dd3': [123, 'x']
#                 }
#             },
#             'm2': {
#                 'x': 123
#             }
#         })
#
#     def test_model_set_3(self):
#         class Model0(mokito.Model):
#             fields = {}
#
#         f = Model0()
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {})
#
#         f['f1'] = 123
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {'f1': 123})
#
#         f['f2'] = ['foo']
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'f1': 123,
#             'f2': ['foo']
#         })
#
#         f['f3'] = ('bar', 123)
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'f1': 123,
#             'f2': ['foo'],
#             'f3': ['bar', 123]
#         })
#
#         f['f4'] = {'a': 1, 'b': 'foo'}
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), {
#             'f1': 123,
#             'f2': ['foo'],
#             'f3': ['bar', 123],
#             'f4': {'a': 1, 'b': 'foo'}
#         })
#
#     def test_model_set_4(self):
#         class Model0(mokito.Model):
#             fields = {}
#
#         f = Model0()
#
#         data = {
#             'f1': 123,
#             'f2': ['foo'],
#             'f3': ('bar', 123),
#             'f4': {'a': 1, 'b': 'foo'}
#         }
#         f.set(data)
#         data['f3'] = list(data['f3'])
#         self.assertDictEqual(f.get(), f.value)
#         self.assertDictEqual(f.get(), data)
#
#     def test_model_query_1(self):
#         class Model0(mokito.Model):
#             fields = {
#                 'd1': int,
#                 'd2': [str],
#                 'd3': (int, str),
#                 'd4': {
#                     'dd1': int,
#                     'dd2': [str],
#                     'dd3': (int, str)
#                 },
#                 'd5': {}
#             }
#
#         f = Model0()
#
#         self.assertDictEqual(f.query, {})
#         f['d1'] = 123
#         self.assertDictEqual(f.query, {'$set': {'d1': 123}})
#         f['d2.0'] = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['123']
#         }})
#         f['d2'][1] = 'foo'
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['123', 'foo']
#         }})
#         f['d2'].append('bar')
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['123', 'foo', 'bar']
#         }})
#         f['d2'].set(['z', 123])
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123']
#         }})
#         f['d3.0'] = 123
#         f['d3.1'] = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [123, '123']
#         }})
#         f['d3'] = [None, 'foo']
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo']
#         }})
#         f['d4.dd1'] = 456
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456
#         }})
#         f['d4.dd2'].append('bar')
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456,
#             'd4.dd2': ['bar']
#         }})
#         f['d4.dd2.2'] = 'x'
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456,
#             'd4.dd2': ['bar', None, 'x']
#         }})
#         f['d4.dd3.1'] = 456
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456,
#             'd4.dd2': ['bar', None, 'x'],
#             'd4.dd3': [None, '456']
#         }})
#         f.dirty_clear()
#         self.assertDictEqual(f.query, {})
#         f.set({
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4.dd1': 123,
#             'd4.dd2': ['a', 'b', 'c'],
#             'd4.dd3': [None, None]
#         }})
#         f['d5'] = {'a': 1, 'b': 'foo'}
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4.dd1': 123,
#             'd4.dd2': ['a', 'b', 'c'],
#             'd4.dd3': [None, None],
#             'd5': {'a': 1, 'b': 'foo'}
#         }})
#         f['d4.dd3.1'] = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4.dd1': 123,
#             'd4.dd2': ['a', 'b', 'c'],
#             'd4.dd3': [None, '123'],
#             'd5': {'a': 1, 'b': 'foo'}
#         }})
#
#     def test_model_query_2(self):
#         class SubModel0(mokito.Model):
#             fields = {
#                 'd1': int,
#                 'd2': [str],
#                 'd4': {
#                     'dd1': int,
#                 },
#                 'd5': {}
#             }
#
#         class SubModel1(mokito.Model):
#             fields = {
#                 'x': int
#             }
#
#         class Model0(mokito.Model):
#             fields = {
#                 'm1': SubModel0,
#                 'm2': SubModel1
#             }
#
#         f = Model0()
#
#         self.assertDictEqual(f.query, {})
#         f['m1.d1'] = 123
#         self.assertDictEqual(f.query, {'$set': {'m1.d1': 123}})
#         f['m1.d2.0'] = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'm1.d1': 123,
#             'm1.d2': ['123']
#         }})
#         f['m1']['d2'][1] = 'foo'
#         self.assertDictEqual(f.query, {'$set': {
#             'm1.d1': 123,
#             'm1.d2': ['123', 'foo']
#         }})
#         f['m1.d2'].set(['z', 123])
#         self.assertDictEqual(f.query, {'$set': {
#             'm1.d1': 123,
#             'm1.d2': ['z', '123']
#         }})
#         f['m1.d4.dd1'] = 456
#         self.assertDictEqual(f.query, {'$set': {
#             'm1.d1': 123,
#             'm1.d2': ['z', '123'],
#             'm1.d4.dd1': 456
#         }})
#         f.dirty_clear()
#         self.assertDictEqual(f.query, {})
#         f.set({
#             'm1': {
#                 'd1': 456,
#                 'd2': ['foo', 'bar'],
#                 'd4': {
#                     'dd1': 123,
#                 }
#             },
#             'm2': {
#                 'x': 123
#             }
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'm1.d1': 456,
#             'm1.d2': ['foo', 'bar'],
#             'm1.d4.dd1': 123,
#             'm2.x': 123
#         }})
#
#     def test_model_field_query_3(self):
#         class Model0(mokito.Model):
#             fields = {}
#
#         f = Model0()
#
#         self.assertDictEqual(f.query, {})
#         f.set({
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         }})
#
#
#
#     # def test_model_roles_1(self):
#     #     class Model0(mokito.Model):
#     #         fields = {
#     #             'd1': int,
#     #             'd2': [datetime.datetime],
#     #             'd3': (int, str),
#     #             'd4': {
#     #                 'dd4': (int, str)
#     #             }
#     #         }
#     #         roles = {
#     #             'r1': ['d1', 'd2'],
#     #             'r2': ['d3.1', 'd4.dd4.1'],
#     #             'r3': ['ad1', '2d1', 'pd2']
#     #         }
#     #         aliases = {
#     #             'ad1': 'd1', '2d1': 'pd1'
#     #         }
#     #
#     #         @property
#     #         def pd1(self):
#     #             return self['d1'].value * 2
#     #
#     #         @property
#     #         def pd2(self):
#     #             return self['d1'].value + 2
#     #
#     #     f = Model0()
#     #
#     #     f.set({
#     #         'd1': 123,
#     #         'd2': [datetime.datetime(2016, 1, 2, 3, 4, 5),
#     #                datetime.datetime(2016, 2, 3, 4, 5, 6),
#     #                datetime.datetime(2016, 3, 4, 5, 6, 7)],
#     #         'd3': (456, 'foo'),
#     #         'd4': {
#     #             'dd4': (111, 'bar')
#     #         }
#     #     })
#     #
#     #     print f.value
#     #     print f.to_json('r1')
