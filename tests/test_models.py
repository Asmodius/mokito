# import unittest
# import datetime
#
# from bson import ObjectId, DBRef
# import mokito
# import tests.util as u
#
#
# class TestModels(unittest.TestCase):
#     def test_model_get_1(self):
#
#         class Model0A(mokito.Model):
#             scheme = {
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
#         f = Model0A()
#         self.assertEqual(f['d1'].value, None)
#         self.assertEqual(f['d1'].self_value, None)
#         self.assertTrue(f == f['d1']._parent)
#         self.assertEqual(f['d2'].value, [])
#         self.assertEqual(f['d2'].self_value, [])
#         self.assertTrue(f == f['d2']._parent)
#         self.assertEqual(f['d3'].value, [None, None])
#         self.assertEqual(f['d3'].self_value, [None, None])
#         self.assertTrue(f == f['d3']._parent)
#         self.assertDictEqual(f['d4'].value, {'dd1': None, 'dd2': [], 'dd3': [None, None]})
#         self.assertDictEqual(f['d4'].self_value, {'dd1': None, 'dd2': [], 'dd3': [None, None]})
#         self.assertEqual(f['d4.dd1'].value, None)
#         self.assertEqual(f['d4.dd1'].self_value, None)
#         self.assertEqual(f['d4']['dd1'].value, None)
#         self.assertEqual(f['d4']['dd1'].self_value, None)
#         self.assertEqual(f['d4.dd2'].value, [])
#         self.assertEqual(f['d4.dd2'].self_value, [])
#         self.assertEqual(f['d4']['dd2'].value, [])
#         self.assertEqual(f['d4']['dd2'].self_value, [])
#         self.assertEqual(f['d4.dd3'].value, [None, None])
#         self.assertEqual(f['d4.dd3'].self_value, [None, None])
#         self.assertEqual(f['d4']['dd3'].value, [None, None])
#         self.assertEqual(f['d4']['dd3'].self_value, [None, None])
#         self.assertTrue(f == f['d4']._parent)
#
#     def test_model_get_2(self):
#         class SubModel0A(mokito.Model):
#             scheme = {
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
#         class SubModel1A(mokito.Model):
#             scheme = {
#                 'x': int
#             }
#
#         class Model1A(mokito.Model):
#             scheme = {
#                 'm1': SubModel0A,
#                 'm2': SubModel1A
#             }
#
#         class Model2A(mokito.Model):
#             scheme = Model1A
#
#         f = Model2A()
#         self.assertEqual(f['m1.d1'].value, None)
#         self.assertEqual(f['m1.d1'].self_value, None)
#         self.assertEqual(f['m1.d2'].value, [])
#         self.assertEqual(f['m1.d2'].self_value, [])
#         self.assertEqual(f['m1.d3'].value, [None, None])
#         self.assertEqual(f['m1.d3'].self_value, [None, None])
#         self.assertDictEqual(f['m1.d4'].value, {'dd1': None, 'dd2': [], 'dd3': [None, None]})
#         self.assertDictEqual(f['m1.d4'].self_value, {'dd1': None, 'dd2': [], 'dd3': [None, None]})
#         self.assertEqual(f['m1.d4.dd1'].value, None)
#         self.assertEqual(f['m1.d4.dd1'].self_value, None)
#         self.assertEqual(f['m1.d4']['dd1'].value, None)
#         self.assertEqual(f['m1.d4']['dd1'].self_value, None)
#         self.assertEqual(f['m1.d4.dd2'].value, [])
#         self.assertEqual(f['m1.d4.dd2'].self_value, [])
#         self.assertEqual(f['m1.d4']['dd2'].value, [])
#         self.assertEqual(f['m1.d4']['dd2'].self_value, [])
#         self.assertEqual(f['m1.d4.dd3'].value, [None, None])
#         self.assertEqual(f['m1.d4.dd3'].self_value, [None, None])
#         self.assertEqual(f['m1.d4']['dd3'].value, [None, None])
#         self.assertEqual(f['m1.d4']['dd3'].self_value, [None, None])
#         self.assertEqual(f['m2']['x'].value, None)
#         self.assertEqual(f['m2']['x'].self_value, None)
#
#     def test_model_set_1(self):
#         class Model0A(mokito.Model):
#             scheme = {
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
#         f = Model0A()
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f['d1'].value = 123
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f['d2.0'].value = 123
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f['d2'][1].value = 'foo'
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f['d2'].append_value('bar')
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f['d2'].set_value(['z', 123])
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd4': {
#                 'dd3': [None, None],
#                 'dd2': [],
#                 'dd1': None
#             },
#             'd3': [None, None]
#         })
#
#         f['d3.0'].value = 123
#         f['d3.1'].value = 123
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [123, '123'],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d3'].value = [None, 'foo']
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': None,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd1'].value = 456
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': [],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd2'].append_value('bar')
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': ['bar'],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd2.2'].value = 'x'
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': ['bar', None, 'x'],
#                 'dd3': [None, None]
#             }
#         })
#
#         f['d4.dd3.1'].value = 456
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [None, 'foo'],
#             'd4': {
#                 'dd1': 456,
#                 'dd2': ['bar', None, 'x'],
#                 'dd3': [None, '456']
#             }
#         })
#
#         f.set_value({
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123, 'x'],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         })
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'd1': 456,
#             'd2': ['foo', 'bar', 'bar'],
#             'd3': [123, 'x'],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, None]
#             }
#         })
#
#     def test_model_set_2(self):
#         class SubModel0A(mokito.Model):
#             scheme = {
#                 'd1': int,
#                 'd2': [str],
#                 'd4': {
#                     'dd3': (int, str)
#                 }
#             }
#
#         class SubModel1A(mokito.Model):
#             scheme = {
#                 'x': int
#             }
#
#         class Model0A(mokito.Model):
#             scheme = {
#                 'm1': SubModel0A,
#                 'm2': SubModel1A
#             }
#
#         class Model1A(mokito.Model):
#             scheme = Model0A
#
#         f = Model1A()
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f['m1']['d1'].value = 123
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f['m1.d2.0'].value = 123
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f['m1']['d2'][1].value = 'foo'
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f['m2'].set_value({'x': 456})
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f['m1.d4.dd3.1'].value = 'x'
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         f.set_value({
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
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
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
#         class Model0A(mokito.Model):
#             scheme = {}
#
#         f = Model0A()
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {})
#
#         f['f1'].value = 123
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {'f1': 123})
#
#         f['f2'].value = ['foo']
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'f1': 123,
#             'f2': ['foo']
#         })
#
#         f['f3'].value = ('bar', 123)
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'f1': 123,
#             'f2': ['foo'],
#             'f3': ['bar', 123]
#         })
#
#         f['f4'].value = {'a': 1, 'b': 'foo'}
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, {
#             'f1': 123,
#             'f2': ['foo'],
#             'f3': ['bar', 123],
#             'f4': {'a': 1, 'b': 'foo'}
#         })
#
#     def test_model_set_4(self):
#         class Model0A(mokito.Model):
#             scheme = {}
#
#         f = Model0A()
#         data = {
#             'f1': 123,
#             'f2': ['foo'],
#             'f3': ('bar', 123),
#             'f4': {'a': 1, 'b': 'foo'}
#         }
#         f.set_value(data)
#         data['f3'] = list(data['f3'])
#         self.assertDictEqual(f.value, f.self_value)
#         self.assertDictEqual(f.value, data)
#
#     def test_model_query_1(self):
#         class Model0A(mokito.Model):
#             scheme = {
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
#         f = Model0A()
#
#         self.assertDictEqual(f.query, {})
#         f['d1'].value = 123
#         self.assertDictEqual(f.query, {'$set': {'d1': 123}})
#         f['d2.0'].value = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['123']
#         }})
#         f['d2'][1].value = 'foo'
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['123', 'foo']
#         }})
#         f['d2'].append_value('bar')
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['123', 'foo', 'bar']
#         }})
#         f['d2'].set_value(['z', 123])
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123', 'bar']
#         }})
#         f['d3.0'].value = 123
#         f['d3.1'].value = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [123, '123']
#         }})
#         f['d3'].value = [None, 'foo']
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [None, 'foo']
#         }})
#         f['d4.dd1'].value = 456
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456
#         }})
#         f['d4.dd2'].append_value('bar')
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456,
#             'd4.dd2': ['bar']
#         }})
#         f['d4.dd2.2'].value = 'x'
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456,
#             'd4.dd2': ['bar', None, 'x']
#         }})
#         f['d4.dd3.1'].value = 456
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 123,
#             'd2': ['z', '123', 'bar'],
#             'd3': [None, 'foo'],
#             'd4.dd1': 456,
#             'd4.dd2': ['bar', None, 'x'],
#             'd4.dd3': [None, '456']
#         }})
#         f.dirty_clear()
#         self.assertDictEqual(f.query, {})
#         f.set_value({
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
#             'd2': ['foo', 'bar', 'bar'],
#             'd3': [123, 'x'],
#             'd4.dd1': 123,
#             'd4.dd2': ['a', 'b', 'c'],
#             'd4.dd3': [None, None]
#         }})
#         f['d5'].value = {'a': 1, 'b': 'foo'}
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar', 'bar'],
#             'd3': [123, 'x'],
#             'd4.dd1': 123,
#             'd4.dd2': ['a', 'b', 'c'],
#             'd4.dd3': [None, None],
#             'd5': {'a': 1, 'b': 'foo'}
#         }})
#         f['d4.dd3.1'].value = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar', 'bar'],
#             'd3': [123, 'x'],
#             'd4.dd1': 123,
#             'd4.dd2': ['a', 'b', 'c'],
#             'd4.dd3': [None, '123'],
#             'd5': {'a': 1, 'b': 'foo'}
#         }})
#
#     def test_model_query_2(self):
#         class SubModel0A(mokito.Model):
#             scheme = {
#                 'd1': int,
#                 'd2': [str],
#                 'd4': {
#                     'dd1': int,
#                 },
#                 'd5': {}
#             }
#
#         class SubModel1A(mokito.Model):
#             scheme = {
#                 'x': int
#             }
#
#         class Model0A(mokito.Model):
#             scheme = {
#                 'm1': SubModel0A,
#                 'm2': SubModel1A
#             }
#
#         f = Model0A()
#         self.assertDictEqual(f.query, {})
#         f['m1.d1'].value = 123
#         self.assertDictEqual(f.query, {'$set': {'m1.d1': 123}})
#         f['m1.d2.0'].value = 123
#         self.assertDictEqual(f.query, {'$set': {
#             'm1.d1': 123,
#             'm1.d2': ['123']
#         }})
#         f['m1']['d2'][1].value = 'foo'
#         self.assertDictEqual(f.query, {'$set': {
#             'm1.d1': 123,
#             'm1.d2': ['123', 'foo']
#         }})
#         f['m1.d2'].set_value(['z', 123])
#         self.assertDictEqual(f.query, {'$set': {
#             'm1.d1': 123,
#             'm1.d2': ['z', '123']
#         }})
#         f['m1.d4.dd1'].value = 456
#         self.assertDictEqual(f.query, {'$set': {
#             'm1.d1': 123,
#             'm1.d2': ['z', '123'],
#             'm1.d4.dd1': 456
#         }})
#         f.dirty_clear()
#         self.assertDictEqual(f.query, {})
#         f.set_value({
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
#         class Model0A(mokito.Model):
#             scheme = {}
#
#         f = Model0A()
#
#         self.assertDictEqual(f.query, {})
#         f.set_value({
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, 123]
#             }
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'd1': 456,
#             'd2': ['foo', 'bar'],
#             'd3': [123],
#             'd4': {
#                 'dd1': 123,
#                 'dd2': ['a', 'b', 'c'],
#                 'dd3': [None, 123]
#             }
#         }})
#
#     def test_model_json(self):
#         class SubModel0A(mokito.Model):
#             scheme = {
#                 'd1': int,
#                 'd2': [{
#                     'a': ObjectId,
#                     'b': datetime.datetime
#                 }]
#             }
#
#         class SubModel1A(mokito.Model):
#             scheme = {
#                 'x': str
#             }
#
#         class Model0A(mokito.Model):
#             scheme = {
#                 'm1': SubModel0A,
#                 'm2': SubModel1A
#             }
#
#             @property
#             def prop1(self):
#                 return self['m1.d1'].value + 2
#
#         class Model1A(mokito.Model):
#             scheme = Model0A
#
#             prop1 = Model0A.prop1
#
#             @property
#             def prop2(self):
#                 return self['m1.d1'].value * 2
#
#         f = Model1A()
#
#         dt1 = datetime.datetime(2015, 1, 2, 3, 4, 5)
#         dt2 = datetime.datetime(2015, 2, 3, 4, 5, 6)
#         id1 = ObjectId()
#         id2 = ObjectId()
#
#         f.set_value({
#             'm1': {
#                 'd1': 456,
#                 'd2': [{'a': id1, 'b': dt1}, {'a': id2, 'b': dt2}],
#             },
#             'm2': {'x': 123}
#         })
#         self.assertDictEqual(f.value, {
#             'm1': {
#                 'd1': 456,
#                 'd2': [{'a': id1, 'b': dt1}, {'a': id2, 'b': dt2}]
#             },
#             'm2': {'x': '123'}
#         })
#         self.assertDictEqual(f.get_value(_date_format='iso', _format='json'), {
#             'm1': {
#                 'd1': 456,
#                 'd2': [{'a': str(id1), 'b': dt1.isoformat()}, {'a': str(id2), 'b': dt2.isoformat()}]
#             },
#             'm2': {'x': '123'}
#         })
#
#     def test_document_1(self):
#         d = u.Document1()
#         self.assertIsNone(d.self_value)
#         self.assertDictEqual(d.value, {
#             '_id': None,
#             'x1': None,
#             'x2': [],
#             'x3': [None, None],
#             'x4': {'a': None, 'b': None}
#         })
#
#         dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
#         dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
#
#         with self.assertRaises(mokito.errors.MokitoChoiceError):
#             d.set_value({
#                 'x1': 123,
#                 'x2': [dt1, dt2],
#                 'x3': [123, 'foo'],
#                 'x4': {'a': 1, 'b': 2}
#             })
#         d.set_value({
#             'x1': 123,
#             'x2': [dt1, dt2],
#             'x3': [123, 1],
#             'x4': {'a': 1, 'b': 2}
#         })
#         self.assertTrue(d.dirty)
#         self.assertIsNone(d.self_value)
#         self.assertDictEqual(d.value, {
#             '_id': None,
#             'x1': 123.0,
#             'x2': [dt1, dt2],
#             'x3': [123, 1],
#             'x4': {'a': 1, 'b': 2}
#         })
#         self.assertDictEqual(d.query, {'$set': {
#             'x1': 123.0,
#             'x2': [dt1, dt2],
#             'x3': [123, 'z1'],
#             'x4.a': 1,
#             'x4.b': 2
#         }})
#
#         d.clear()
#         self.assertDictEqual(d.query, {
#             '$set': {
#                 'x1': None,
#                 'x2': [],
#                 'x3': [None, None],
#                 'x4.a': None,
#                 'x4.b': None
#             }
#         })
#
#         d['x1'].value = 123
#         d.dirty_clear()
#         self.assertFalse(d.dirty)
#         self.assertEqual(d.query, {})
#
#         self.assertEqual(125.0, d.prop1)
#         self.assertEqual(246.0, d.prop2)
#         self.assertIsNone(d._id)
#
#     def test_document_2(self):
#         d = u.Document2()
#         self.assertIsNone(d.self_value)
#         self.assertDictEqual(d.value, {
#             '_id': None,
#             'f1': [None, None],
#             'f2': {'a': None, 'b': None},
#             'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
#             'm2': [],
#             'd2': [],
#             'd1': {'_id': None, 'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}}
#         })
#
#         dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
#         dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
#
#         d.set_value({
#             'f1': [111, 'x'],
#             'f2': {'a': 222, 'b': None},
#         })
#         self.assertIsNone(d.self_value)
#         self.assertDictEqual(d.value, {
#             '_id': None,
#             'f1': [111, 'x'],
#             'f2': {'a': 222, 'b': None},
#             'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
#             'm2': [],
#             'd1': {'_id': None, 'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
#             'd2': []
#         })
#
#         self.assertDictEqual(d.query, {'$set': {
#             'f1': [111, 'x'],
#             'f2.a': 222
#         }})
#
#         d['m1'].value = {'x1': 1, 'x2': [dt1], 'x3': [2, None], 'x4': {'a': 3, 'b': None}}
#         self.assertDictEqual(d.query, {'$set': {
#             'f1': [111, 'x'],
#             'f2.a': 222,
#             'm1.x1': 1.0,
#             'm1.x2': [dt1],
#             'm1.x3': [2, None],
#             'm1.x4.a': 3
#         }})
#
#         d['m2'].append_value({'x1': 1, 'x2': [dt1], 'x3': [2, None], 'x4': {'a': 3, 'b': None}})
#         self.assertDictEqual(d.query, {'$set': {
#             'f1': [111, 'x'],
#             'f2.a': 222,
#             'm1.x1': 1.0,
#             'm1.x2': [dt1],
#             'm1.x3': [2, None],
#             'm1.x4.a': 3,
#             'm2': [{
#                 'x2': [dt1],
#                 'x3': [2, None],
#                 'x1': 1.0,
#                 'x4': {'a': 3, 'b': None}}]
#         }})
#
#         d['m1.x2'].value = [dt2, dt1]
#         self.assertDictEqual(d.query, {'$set': {
#             'f1': [111, 'x'],
#             'f2.a': 222,
#             'm1.x1': 1.0,
#             'm1.x2': [dt2, dt1],
#             'm1.x3': [2, None],
#             'm1.x4.a': 3,
#             'm2': [{
#                 'x2': [dt1],
#                 'x3': [2, None],
#                 'x1': 1.0,
#                 'x4': {'a': 3, 'b': None}}]
#         }})
#
#         self.assertEqual(d['m1'].prop1, 3.0)
#         self.assertEqual(d['m2.0'].prop1, 3.0)
#         d['m1.x1'].value = 10
#         d['m2.0.x1'].value = 20
#         self.assertEqual(d['m1'].prop1, 12.0)
#         self.assertEqual(d['m2.0'].prop1, 22.0)
#
#     def test_document_3(self):
#         dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
#
#         d = u.Document2()
#         # scheme = {
#         #     'f1': (int, str),
#         #     'f2': {'a': int, 'b': int},
#         #     'm1': Model1,
#         #     'm2': [Model1],
#         #     'd1': Document1, ->Model1
#         #     'd2': [Document1] ->[Model1]
#         # }
#
#         d['d1'].value = {'x1': 100, 'x2': [dt2], 'x3': (200, 3), 'x4': {'b': 300}}
#         self.assertFalse(d.dirty)
#         self.assertIsNone(d.self_value)
#         self.assertDictEqual(d.value, {
#             '_id': None,
#             'f1': [None, None],
#             'f2': {'a': None, 'b': None},
#             'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
#             'm2': [],
#             'd1': {'_id': None, 'x1': 100.0, 'x2': [dt2], 'x3': [200, 3], 'x4': {'a': None, 'b': 300}},
#             'd2': []
#         })
#
#         self.assertEqual(d.query, {})
#         # with self.assertRaises(mokito.errors.MokitoDBREFError):
#         #     _ = d.query
#
#         id1 = ObjectId()
#         d['d1'].id = id1
#         self.assertDictEqual(d.query, {'$set': {'d1': DBRef(u.Document1.__collection__, id1)}})
#
#         d.dirty_clear()
#         self.assertFalse(d.dirty)
#         self.assertDictEqual(d.query, {'$set': {'d1': DBRef(u.Document1.__collection__, id1)}})
#
#         d['d1'].dirty_clear()
#         d['d1.x4.a'].value = 500
#         self.assertFalse(d.dirty)
#         self.assertDictEqual(d.query, {})
#         self.assertTrue(d['d1'].dirty)
#         self.assertDictEqual(d['d1'].query, {'$set': {'x4.a': 500}})
#
#         # # d['d1'].value = None
#         # # d['d1'] = None
#         del d['d1']
#         self.assertTrue(d.dirty)
#         self.assertDictEqual(d.query, {'$unset': {'d1': ''}})
#
#         # d['f1'].value = None
#         # d['f1'] = None
#         del d['f1']
#         self.assertTrue(d.dirty)
#         self.assertDictEqual(d.query, {'$set': {'f1': [None, None]}, '$unset': {'d1': ''}})
#
#         del d['f2']
#         self.assertTrue(d.dirty)
#         self.assertDictEqual(d.query, {'$set': {'f1': [None, None], 'f2.a': None, 'f2.b': None}, '$unset': {'d1': ''}})
#
#         del d['m1']
#         self.assertTrue(d.dirty)
#         self.assertDictEqual(d.query, {
#             '$set': {
#                 'f1': [None, None],
#                 'f2.a': None, 'f2.b': None,
#                 'm1.x1': None, 'm1.x2': [], 'm1.x3': [None, None], 'm1.x4.a': None, 'm1.x4.b': None
#             },
#             '$unset': {'d1': ''}
#         })
#
#         del d['m2']
#         self.assertTrue(d.dirty)
#         self.assertDictEqual(d.query, {
#             '$set': {
#                 'f1': [None, None],
#                 'f2.a': None, 'f2.b': None,
#                 'm1.x1': None, 'm1.x2': [], 'm1.x3': [None, None], 'm1.x4.a': None, 'm1.x4.b': None,
#                 'm2': []
#             },
#             '$unset': {'d1': ''}
#         })
#
#         d.dirty_clear()
#         del d['d2']
#         self.assertTrue(d.dirty)
#         self.assertDictEqual(d.query, {'$set': {'d2': []}})
#
#     def test_document_4(self):
#         dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
#         dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
#         id1 = ObjectId()
#         id2 = ObjectId()
#
#         d = u.Document2()
#         # scheme = {
#         #     'f1': (int, str),
#         #     'f2': {'a': int, 'b': int},
#         #     'm1': Model1,
#         #     'm2': [Model1],
#         #     'd1': Document1,
#         #     'd2': [Document1]
#         # }
#
#         d['d2'].append_value({'x1': 100, 'x2': [dt1], 'x3': (200, 1), 'x4': {'b': 300}})
#         self.assertTrue(d.dirty)
#         self.assertIsNone(d.self_value)
#
#         self.assertDictEqual(d.value, {
#             '_id': None,
#             'f1': [None, None],
#             'f2': {'a': None, 'b': None},
#             'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
#             'm2': [],
#             'd1': {'_id': None, 'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
#             'd2': [{'_id': None, 'x1': 100.0, 'x2': [dt1], 'x3': [200, 1], 'x4': {'a': None, 'b': 300}}],
#         })
#
#         with self.assertRaises(mokito.errors.MokitoDBREFError):
#             _ = d.query
#
#         d['d2.0'].id = id1
#         d['d2.0'].dirty_clear()
#
#         self.assertTrue(d.dirty)
#         self.assertDictEqual(d.query, {'$set': {'d2': [DBRef(u.Document1.__collection__, id1)]}})
#
#         d.dirty_clear()
#         d['d2'][1].value = {'x1': 200.0, 'x2': [dt2], 'x3': [300, 2], 'x4': {'a': None, 'b': 400}}
#         with self.assertRaises(mokito.errors.MokitoDBREFError):
#             _ = d.query
#
#         d['d2.1'].id = id2
#         d['d2.1'].dirty_clear()
#         self.assertTrue(d.dirty)
#         self.assertDictEqual(d.query, {'$set': {'d2': [DBRef(u.Document1.__collection__, id1),
#                                                        DBRef(u.Document1.__collection__, id2)]}})
#         del d['d2.0']
#         self.assertDictEqual(d.query, {'$set': {'d2': [DBRef(u.Document1.__collection__, id2)]}})
#
#         d.dirty_clear()
#         d['d2.0.x1'].value = 55
#         self.assertFalse(d.dirty)
#         self.assertDictEqual(d.query, {})
#
#         self.assertDictEqual(d['d2'].value[0],
#                              {'_id': id2, 'x2': [dt2], 'x3': [300, 2], 'x1': 55.0, 'x4': {'a': None, 'b': 400}})
#         self.assertEqual(d['d2'].self_value[0], DBRef(u.Document1.__collection__, id2))
#
#     def test_model_choices(self):
#         from mokito.fields import ChoiceField
#         ch1 = ['foo', 'bar']
#         ch2 = {'x': 1, 'y': 2}
#         ch3 = {'a': 100, 'b': 200}
#
#         class Model0B(mokito.Model):
#             scheme = {
#                 'd1': ChoiceField(ch1),
#                 'd2': [ChoiceField(ch2)],
#                 'd3': (int, ChoiceField(ch3)),
#                 'd4': {
#                     'dd1': ChoiceField(ch1),
#                     'dd2': [ChoiceField(ch2)],
#                     'dd3': (int, ChoiceField(ch3))
#                 }
#             }
#
#         f = Model0B()
#         f['d1'].value = 'foo'
#         f['d2'].append_value(1)
#         f['d3.1'].value = 100
#         f['d4.dd1'].value = 'foo'
#         f['d4.dd2'].append_value(1)
#         f['d4.dd3.1'].value = 100
#         self.assertDictEqual(f.value, {
#             'd1': 'foo',
#             'd2': [1],
#             'd3': [None, 100],
#             'd4': {
#                 'dd1': 'foo',
#                 'dd2': [1],
#                 'dd3': [None, 100]
#             }
#         })
#         self.assertDictEqual(f.self_value, {
#             'd1': 'foo',
#             'd2': ['x'],
#             'd3': [None, 'a'],
#             'd4': {
#                 'dd1': 'foo',
#                 'dd2': ['x'],
#                 'dd3': [None, 'a']
#             }
#         })
#
#         f.set_value({
#             'd1': 'bar',
#             'd2': [2],
#             'd3': [None, 200],
#             'd4': {
#                 'dd1': 'bar',
#                 'dd2': [2],
#                 'dd3': [None, 200]
#             }
#         })
#         self.assertDictEqual(f.value, {
#             'd1': 'bar',
#             'd2': [2],
#             'd3': [None, 200],
#             'd4': {
#                 'dd1': 'bar',
#                 'dd2': [2],
#                 'dd3': [None, 200]
#             }
#         })
#         self.assertDictEqual(f.self_value, {
#             'd1': 'bar',
#             'd2': ['y'],
#             'd3': [None, 'b'],
#             'd4': {
#                 'dd1': 'bar',
#                 'dd2': ['y'],
#                 'dd3': [None, 'b']
#             }
#         })
#
#         f.clear()
#         f.set_value({
#             'd1': 'foo',
#             'd2': ['x'],
#             'd3': [None, 'a'],
#             'd4': {
#                 'dd1': 'foo',
#                 'dd2': ['x'],
#                 'dd3': [None, 'a']
#             }
#         }, inner=True)
#         self.assertDictEqual(f.value, {
#             'd1': 'foo',
#             'd2': [1],
#             'd3': [None, 100],
#             'd4': {
#                 'dd1': 'foo',
#                 'dd2': [1],
#                 'dd3': [None, 100]
#             }
#         })
#         self.assertDictEqual(f.self_value, {
#             'd1': 'foo',
#             'd2': ['x'],
#             'd3': [None, 'a'],
#             'd4': {
#                 'dd1': 'foo',
#                 'dd2': ['x'],
#                 'dd3': [None, 'a']
#             }
#         })
#
#     def test_list_model(self):
#
#         class Model1L(mokito.Model):
#             scheme = {
#                 'a1': 123,
#                 'a2': ['foo'],
#             }
#
#         class Model2L(mokito.Model):
#             scheme = {
#                 'b1': [Model1L],
#                 'b2': (456, Model1L)
#             }
#
#         f = Model2L()
#         self.assertDictEqual(f.value, {
#             'b1': [{'a1': 123, 'a2': ['foo']}],
#             'b2': [456, {'a1': 123, 'a2': ['foo']}]
#         })
#
#         # self.assertDictEqual(f.query, {'$set': {'b2': [456, {'a1': 123, 'a2': ['foo']}]}})
#         self.assertDictEqual(f.query, {})
#
#         f['b1.1.a1'].value = 111
#         self.assertDictEqual(f.value, {
#             'b1': [{'a1': 123, 'a2': ['foo']}, {'a1': 111, 'a2': ['foo']}],
#             'b2': [456, {'a1': 123, 'a2': ['foo']}]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'b1': [{'a1': 123, 'a2': ['foo']}, {'a1': 111, 'a2': ['foo']}]}
#         })
#
#         x = Model1L()
#         x.set_value({'a1': 222, 'a2': ['bar', 'baz']})
#         f['b1'].append(x)
#         self.assertDictEqual(f.value, {
#             'b1': [{'a1': 123, 'a2': ['foo']},
#                    {'a1': 111, 'a2': ['foo']},
#                    {'a1': 222, 'a2': ['bar', 'baz']}],
#             'b2': [456, {'a1': 123, 'a2': ['foo']}]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'b1': [{'a1': 123, 'a2': ['foo']},
#                    {'a1': 111, 'a2': ['foo']},
#                    {'a1': 222, 'a2': ['bar', 'baz']}]}
#         })
#
#     def test_list_document(self):
#         class Model1D(mokito.Model):
#             scheme = {
#                 'a': [u.Document1],
#             }
#         f = Model1D()
#         self.assertDictEqual(f.value, {'a': []})
#         self.assertDictEqual(f.query, {})
#
#         f['a.0.x1'].value = 1
#         self.assertDictEqual(f.value, {
#             'a': [{'x1': 1.0, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}, '_id': None}]})
#         with self.assertRaises(mokito.errors.MokitoDBREFError):
#             _ = f.query
#         self.assertDictEqual(f['a.0'].value, {
#             '_id': None,
#             'x1': 1.0,
#             'x2': [],
#             'x3': [None, None],
#             'x4': {'a': None, 'b': None}
#         })
#         self.assertDictEqual(f['a.0'].query, {'$set': {'x1': 1.0}})
