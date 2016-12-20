# coding: utf-8

import unittest
import datetime

from bson import ObjectId, DBRef
import mokito


class TestModels(unittest.TestCase):
    def test_model_get_1(self):
        class Model_0(mokito.Model):
            fields = {
                'd1': int,
                'd2': [str],
                'd3': (int, str),
                'd4': {
                    'dd1': int,
                    'dd2': [str],
                    'dd3': (int, str)
                }
            }

        f = Model_0()

        self.assertEqual(f['d1'].get(), None)
        self.assertEqual(f['d1'].value, None)
        self.assertEqual(f['d2'].get(), [])
        self.assertEqual(f['d2'].value, [])
        self.assertEqual(f['d3'].get(), [None, None])
        self.assertEqual(f['d3'].value, [None, None])
        self.assertDictEqual(f['d4'].get(), {'dd1': None, 'dd2': [], 'dd3': [None, None]})
        self.assertDictEqual(f['d4'].value, {'dd1': None, 'dd2': [], 'dd3': [None, None]})
        self.assertEqual(f['d4.dd1'].get(), None)
        self.assertEqual(f['d4.dd1'].value, None)
        self.assertEqual(f['d4']['dd1'].get(), None)
        self.assertEqual(f['d4']['dd1'].value, None)
        self.assertEqual(f['d4.dd2'].get(), [])
        self.assertEqual(f['d4.dd2'].value, [])
        self.assertEqual(f['d4']['dd2'].get(), [])
        self.assertEqual(f['d4']['dd2'].value, [])
        self.assertEqual(f['d4.dd3'].get(), [None, None])
        self.assertEqual(f['d4.dd3'].value, [None, None])
        self.assertEqual(f['d4']['dd3'].get(), [None, None])
        self.assertEqual(f['d4']['dd3'].value, [None, None])

    def test_model_get_2(self):
        class SubModel_0(mokito.Model):
            fields = {
                'd1': int,
                'd2': [str],
                'd3': (int, str),
                'd4': {
                    'dd1': int,
                    'dd2': [str],
                    'dd3': (int, str)
                }
            }

        class SubModel_1(mokito.Model):
            fields = {
                'x': int
            }

        class Model1(mokito.Model):
            fields = {
                'm1': SubModel_0,
                'm2': SubModel_1
            }

        class Model_2(mokito.Model):
            fields = Model1

        f = Model_2()

        self.assertEqual(f['m1.d1'].get(), None)
        self.assertEqual(f['m1.d1'].value, None)
        self.assertEqual(f['m1.d2'].get(), [])
        self.assertEqual(f['m1.d2'].value, [])
        self.assertEqual(f['m1.d3'].get(), [None, None])
        self.assertEqual(f['m1.d3'].value, [None, None])
        self.assertDictEqual(f['m1.d4'].get(), {'dd1': None, 'dd2': [], 'dd3': [None, None]})
        self.assertDictEqual(f['m1.d4'].value, {'dd1': None, 'dd2': [], 'dd3': [None, None]})
        self.assertEqual(f['m1.d4.dd1'].get(), None)
        self.assertEqual(f['m1.d4.dd1'].value, None)
        self.assertEqual(f['m1.d4']['dd1'].get(), None)
        self.assertEqual(f['m1.d4']['dd1'].value, None)
        self.assertEqual(f['m1.d4.dd2'].get(), [])
        self.assertEqual(f['m1.d4.dd2'].value, [])
        self.assertEqual(f['m1.d4']['dd2'].get(), [])
        self.assertEqual(f['m1.d4']['dd2'].value, [])
        self.assertEqual(f['m1.d4.dd3'].get(), [None, None])
        self.assertEqual(f['m1.d4.dd3'].value, [None, None])
        self.assertEqual(f['m1.d4']['dd3'].get(), [None, None])
        self.assertEqual(f['m1.d4']['dd3'].value, [None, None])

        self.assertEqual(f['m2']['x'].value, None)

    def test_model_set_1(self):
        class Model_0(mokito.Model):
            fields = {
                'd1': int,
                'd2': [str],
                'd3': (int, str),
                'd4': {
                    'dd1': int,
                    'dd2': [str],
                    'dd3': (int, str)
                }
            }

        f = Model_0()
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': None,
            'd2': [],
            'd3': [None, None],
            'd4': {
                'dd1': None,
                'dd2': [],
                'dd3': [None, None]
            }
        })

        f['d1'] = 123
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': [],
            'd3': [None, None],
            'd4': {
                'dd1': None,
                'dd2': [],
                'dd3': [None, None]
            }
        })

        f['d2.0'] = 123
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': ['123'],
            'd3': [None, None],
            'd4': {
                'dd1': None,
                'dd2': [],
                'dd3': [None, None]
            }
        })

        f['d2'][1] = 'foo'
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': ['123', 'foo'],
            'd3': [None, None],
            'd4': {
                'dd1': None,
                'dd2': [],
                'dd3': [None, None]
            }
        })

        f['d2'].append('bar')
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': ['123', 'foo', 'bar'],
            'd3': [None, None],
            'd4': {
                'dd1': None,
                'dd2': [],
                'dd3': [None, None]
            }
        })

        f['d2'].set(['z', 123])
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd4': {
                'dd3': [None, None],
                'dd2': [],
                'dd1': None
            },
            'd3': [None, None]
        })

        f['d3.0'] = 123
        f['d3.1'] = 123
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [123, '123'],
            'd4': {
                'dd1': None,
                'dd2': [],
                'dd3': [None, None]
            }
        })

        f['d3'] = [None, 'foo']
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4': {
                'dd1': None,
                'dd2': [],
                'dd3': [None, None]
            }
        })

        f['d4.dd1'] = 456
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4': {
                'dd1': 456,
                'dd2': [],
                'dd3': [None, None]
            }
        })

        f['d4.dd2'].append('bar')
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4': {
                'dd1': 456,
                'dd2': ['bar'],
                'dd3': [None, None]
            }
        })

        f['d4.dd2.2'] = 'x'
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4': {
                'dd1': 456,
                'dd2': ['bar', None, 'x'],
                'dd3': [None, None]
            }
        })

        f['d4.dd3.1'] = 456
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4': {
                'dd1': 456,
                'dd2': ['bar', None, 'x'],
                'dd3': [None, '456']
            }
        })

        f.set({
            'd1': 456,
            'd2': ['foo', 'bar'],
            'd3': [123, 'x'],
            'd4': {
                'dd1': 123,
                'dd2': ['a', 'b', 'c'],
                'dd3': [None, None]
            }
        })
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'd1': 456,
            'd2': ['foo', 'bar', 'bar'],
            'd3': [123, 'x'],
            'd4': {
                'dd1': 123,
                'dd2': ['a', 'b', 'c'],
                'dd3': [None, None]
            }
        })

    def test_model_set_2(self):
        class SubModel_0(mokito.Model):
                fields = {
                    'd1': int,
                    'd2': [str],
                    'd4': {
                        'dd3': (int, str)
                    }
                }

        class SubModel_1(mokito.Model):
            fields = {
                'x': int
            }

        class Model_0(mokito.Model):
            fields = {
                'm1': SubModel_0,
                'm2': SubModel_1
            }

        class Model_1(mokito.Model):
            fields = Model_0

        f = Model_1()
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'm1': {
                'd1': None,
                'd2': [],
                'd4': {
                    'dd3': [None, None]
                }
            },
            'm2': {
                'x': None
            }
        })

        f['m1']['d1'] = 123
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'm1': {
                'd1': 123,
                'd2': [],
                'd4': {
                    'dd3': [None, None]
                }
            },
            'm2': {
                'x': None
            }
        })

        f['m1.d2.0'] = 123
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'm1': {
                'd1': 123,
                'd2': ['123'],
                'd4': {
                    'dd3': [None, None]
                }
            },
            'm2': {
                'x': None
            }
        })

        f['m1']['d2'][1] = 'foo'
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'm1': {
                'd1': 123,
                'd2': ['123', 'foo'],
                'd4': {
                    'dd3': [None, None]
                }
            },
            'm2': {
                'x': None
            }
        })

        f['m2'].set({'x': 456})

        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'm1': {
                'd1': 123,
                'd2': ['123', 'foo'],
                'd4': {
                    'dd3': [None, None]
                }
            },
            'm2': {
                'x': 456
            }
        })

        f['m1.d4.dd3.1'] = 'x'
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'm1': {
                'd1': 123,
                'd2': ['123', 'foo'],
                'd4': {
                    'dd3': [None, 'x']
                }
            },
            'm2': {
                'x': 456
            }
        })

        f.set({
            'm1': {
                'd1': 456,
                'd2': ['foo', 'bar'],
                'd4': {
                    'dd3': [123, 'x']
                }
            },
            'm2': {
                'x': 123
            }
        })
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'm1': {
                'd1': 456,
                'd2': ['foo', 'bar'],
                'd4': {
                    'dd3': [123, 'x']
                }
            },
            'm2': {
                'x': 123
            }
        })

    def test_model_set_3(self):
        class Model_0(mokito.Model):
            fields = {}

        f = Model_0()
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {})

        f['f1'] = 123
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {'f1': 123})

        f['f2'] = ['foo']
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'f1': 123,
            'f2': ['foo']
        })

        f['f3'] = ('bar', 123)
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'f1': 123,
            'f2': ['foo'],
            'f3': ['bar', 123]
        })

        f['f4'] = {'a': 1, 'b': 'foo'}
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), {
            'f1': 123,
            'f2': ['foo'],
            'f3': ['bar', 123],
            'f4': {'a': 1, 'b': 'foo'}
        })

    def test_model_set_4(self):
        class Model_0(mokito.Model):
            fields = {}

        f = Model_0()

        data = {
            'f1': 123,
            'f2': ['foo'],
            'f3': ('bar', 123),
            'f4': {'a': 1, 'b': 'foo'}
        }
        f.set(data)
        data['f3'] = list(data['f3'])
        self.assertDictEqual(f.get(), f.value)
        self.assertDictEqual(f.get(), data)

    def test_model_query_1(self):
        class Model_0(mokito.Model):
            fields = {
                'd1': int,
                'd2': [str],
                'd3': (int, str),
                'd4': {
                    'dd1': int,
                    'dd2': [str],
                    'dd3': (int, str)
                },
                'd5': {}
            }

        f = Model_0()

        self.assertDictEqual(f.query, {})
        f['d1'] = 123
        self.assertDictEqual(f.query, {'$set': {'d1': 123}})
        f['d2.0'] = 123
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['123']
        }})
        f['d2'][1] = 'foo'
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['123', 'foo']
        }})
        f['d2'].append('bar')
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['123', 'foo', 'bar']
        }})
        f['d2'].set(['z', 123])
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar']
        }})
        f['d3.0'] = 123
        f['d3.1'] = 123
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [123, '123']
        }})
        f['d3'] = [None, 'foo']
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo']
        }})
        f['d4.dd1'] = 456
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456
        }})
        f['d4.dd2'].append('bar')
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456,
            'd4.dd2': ['bar']
        }})
        f['d4.dd2.2'] = 'x'
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456,
            'd4.dd2': ['bar', None, 'x']
        }})
        f['d4.dd3.1'] = 456
        self.assertDictEqual(f.query, {'$set': {
            'd1': 123,
            'd2': ['z', '123', 'bar'],
            'd3': [None, 'foo'],
            'd4.dd1': 456,
            'd4.dd2': ['bar', None, 'x'],
            'd4.dd3': [None, '456']
        }})
        f.dirty_clear()
        self.assertDictEqual(f.query, {})
        f.set({
            'd1': 456,
            'd2': ['foo', 'bar'],
            'd3': [123, 'x'],
            'd4': {
                'dd1': 123,
                'dd2': ['a', 'b', 'c'],
                'dd3': [None, None]
            }
        })
        self.assertDictEqual(f.query, {'$set': {
            'd1': 456,
            'd2': ['foo', 'bar', 'bar'],
            'd3': [123, 'x'],
            'd4.dd1': 123,
            'd4.dd2': ['a', 'b', 'c'],
            'd4.dd3': [None, None]
        }})
        f['d5'] = {'a': 1, 'b': 'foo'}
        self.assertDictEqual(f.query, {'$set': {
            'd1': 456,
            'd2': ['foo', 'bar', 'bar'],
            'd3': [123, 'x'],
            'd4.dd1': 123,
            'd4.dd2': ['a', 'b', 'c'],
            'd4.dd3': [None, None],
            'd5': {'a': 1, 'b': 'foo'}
        }})
        f['d4.dd3.1'] = 123
        self.assertDictEqual(f.query, {'$set': {
            'd1': 456,
            'd2': ['foo', 'bar', 'bar'],
            'd3': [123, 'x'],
            'd4.dd1': 123,
            'd4.dd2': ['a', 'b', 'c'],
            'd4.dd3': [None, '123'],
            'd5': {'a': 1, 'b': 'foo'}
        }})

    def test_model_query_2(self):
        class SubModel_0(mokito.Model):
            fields = {
                'd1': int,
                'd2': [str],
                'd4': {
                    'dd1': int,
                },
                'd5': {}
            }

        class SubModel_1(mokito.Model):
            fields = {
                'x': int
            }

        class Model_0(mokito.Model):
            fields = {
                'm1': SubModel_0,
                'm2': SubModel_1
            }

        f = Model_0()

        self.assertDictEqual(f.query, {})
        f['m1.d1'] = 123
        self.assertDictEqual(f.query, {'$set': {'m1.d1': 123}})
        f['m1.d2.0'] = 123
        self.assertDictEqual(f.query, {'$set': {
            'm1.d1': 123,
            'm1.d2': ['123']
        }})
        f['m1']['d2'][1] = 'foo'
        self.assertDictEqual(f.query, {'$set': {
            'm1.d1': 123,
            'm1.d2': ['123', 'foo']
        }})
        f['m1.d2'].set(['z', 123])
        self.assertDictEqual(f.query, {'$set': {
            'm1.d1': 123,
            'm1.d2': ['z', '123']
        }})
        f['m1.d4.dd1'] = 456
        self.assertDictEqual(f.query, {'$set': {
            'm1.d1': 123,
            'm1.d2': ['z', '123'],
            'm1.d4.dd1': 456
        }})
        f.dirty_clear()
        self.assertDictEqual(f.query, {})
        f.set({
            'm1': {
                'd1': 456,
                'd2': ['foo', 'bar'],
                'd4': {
                    'dd1': 123,
                }
            },
            'm2': {
                'x': 123
            }
        })
        self.assertDictEqual(f.query, {'$set': {
            'm1.d1': 456,
            'm1.d2': ['foo', 'bar'],
            'm1.d4.dd1': 123,
            'm2.x': 123
        }})

    def test_model_field_query_3(self):
        class Model_0(mokito.Model):
            fields = {}

        f = Model_0()

        self.assertDictEqual(f.query, {})
        f.set({
            'd1': 456,
            'd2': ['foo', 'bar'],
            'd3': [123],
            'd4': {
                'dd1': 123,
                'dd2': ['a', 'b', 'c'],
                'dd3': [None, None]
            }
        })
        self.assertDictEqual(f.query, {'$set': {
            'd1': 456,
            'd2': ['foo', 'bar'],
            'd3': [123],
            'd4': {
                'dd1': 123,
                'dd2': ['a', 'b', 'c'],
                'dd3': [None, None]
            }
        }})

    def test_model_json(self):
        class SubModel_0(mokito.Model):
                fields = {
                    'd1': int,
                    'd2': [{
                        'a': ObjectId,
                        'b': datetime.datetime
                    }]
                }

        class SubModel_1(mokito.Model):
            fields = {
                'x': str
            }

        class Model_0(mokito.Model):
            fields = {
                'm1': SubModel_0,
                'm2': SubModel_1
            }

            @property
            def prop1(self):
                return self['m1.d1'].value + 2

        class Model_1(mokito.Model):
            fields = Model_0

            prop1 = Model_0.prop1

            @property
            def prop2(self):
                return self['m1.d1'].value * 2

        f = Model_1()

        dt1 = datetime.datetime(2015, 1, 2, 3, 4, 5)
        dt2 = datetime.datetime(2015, 2, 3, 4, 5, 6)
        id1 = ObjectId()
        id2 = ObjectId()

        f.set({
            'm1': {
                'd1': 456,
                'd2': [{'a': id1, 'b': dt1}, {'a': id2, 'b': dt2}],
            },
            'm2': {
                'x': 123
            }
        })

        self.assertDictEqual(f.get(), {
            'm1': {
                'd1': 456,
                'd2': [
                    {'a': id1, 'b': dt1},
                    {'a': id2, 'b': dt2}
                ]
            },
            'm2': {'x': '123'}
        })
        self.assertDictEqual(f.get(date_format='iso', as_json=True), {
            'm1': {
                'd1': 456,
                'd2': [
                    {'a': str(id1), 'b': dt1.isoformat()},
                    {'a': str(id2), 'b': dt2.isoformat()}
                ]
            },
            'm2': {'x': '123'}
        })
        param = {'date_format': 'iso', 'as_json': True, 'flat': True}
        self.assertDictEqual(f.get(**param), {
            'm1.d1': 456,
            'm1.d2.0.a': str(id1),
            'm1.d2.0.b': dt1.isoformat(),
            'm1.d2.1.a': str(id2),
            'm1.d2.1.b': dt2.isoformat(),
            'm2.x': '123'
        })

        param = {'date_format': 'iso', 'as_json': True, 'flat': True,
                 'aliases': {'m1.d1': 'f1', 'm1.d2.0.a': 'f2', 'm1.d2.0.b':
                             'f3', 'm1.d2.1.a': 'f4', 'm1.d2.1.b': 'f5', 'm2.x': 'f6'}}
        self.assertDictEqual(f.get(**param), {
            'f1': 456,
            'f2': str(id1),
            'f3': dt1.isoformat(),
            'f4': str(id2),
            'f5': dt2.isoformat(),
            'f6': '123'
        })

        param = {'date_format': 'iso', 'as_json': True, 'flat': True,
                 'aliases': {'m1.d1': 'f1', 'm1.d2.0.a': 'f2', 'm1.d2.1.b': 'f3',
                             'prop1': 'f4', 'prop2': 'f5', 'm2.x': 'f6'},
                 'fields': ['m1.d1', 'm1.d2.0.a', 'm1.d2.1.b', 'm2', 'prop1', 'prop2']}
        self.assertDictEqual(f.get(**param), {
            'f1': 456,
            'f2': str(id1),
            'f3': dt2.isoformat(),
            'f4': 456 + 2,
            'f5': 456 * 2,
            'f6': '123'
        })

        f.clear()
        f.set({
            'f1': 456,
            '0a': str(id1),
            '0b': dt1.isoformat(),
            '1a': str(id2),
            '1b': dt2.isoformat(),
            'f2': '123'
        }, {'f1': 'm1.d1', 'f2': 'm2.x', '0a': 'm1.d2.0.a', '0b': 'm1.d2.0.b', '1a': 'm1.d2.1.a', '1b': 'm1.d2.1.b'})

        self.assertDictEqual(f.get(), {
            'm1': {
                'd1': 456,
                'd2': [
                    {'a': id1, 'b': dt1},
                    {'a': id2, 'b': dt2}
                ]
            },
            'm2': {'x': '123'}
        })

        f.clear()
        f.set({
            'f1': 456,
            'f3': {'a': str(id1), 'b': dt1.isoformat()},
            'f4': {'a': str(id2), 'b': dt2.isoformat()},
            'f2': '123',
        }, {'f1': 'm1.d1', 'f2': 'm2.x', 'f3': 'm1.d2.0', 'f4': 'm1.d2.1'})
        self.assertDictEqual(f.value, {
            'm1': {
                'd1': 456,
                'd2': [
                    {'a': id1, 'b': dt1},
                    {'a': id2, 'b': dt2}
                ]
            },
            'm2': {'x': '123'}
        })

    def test_document_1(self):
        from tests.util import Document1

        d = Document1()
        self.assertDictEqual(d.value, {
            'x1': None,
            'x2': [],
            'x3': [None, None],
            'x4': {'a': None, 'b': None}
        })

        dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
        dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
        with self.assertRaises(mokito.errors.MokitoChoiceError):
            d.set({
                'x1': 123,
                'x2': [dt1, dt2],
                'x3': [123, 'foo'],
                'x4': {'a': 1, 'b': 2}
            })
        d.set({
            'x1': 123,
            'x2': [dt1, dt2],
            'x3': [123, 1],
            'x4': {'a': 1, 'b': 2}
        })
        self.assertTrue(d.dirty)
        self.assertDictEqual(d.value, {
            'x1': 123.0,
            'x2': [dt1, dt2],
            'x3': [123, 'z1'],
            'x4': {'a': 1, 'b': 2}
        })
        self.assertDictEqual(d.query, {'$set': {
            'x1': 123.0,
            'x2': [dt1, dt2],
            'x3': [123, 'z1'],
            'x4.a': 1,
            'x4.b': 2
        }})

        d.clear()
        self.assertDictEqual(d.query, {
            '$set': {
                'x1': None,
                'x2': [],
                'x3': [None, None],
                'x4.a': None,
                'x4.b': None
            }
        })

        d.set({
            'f1': 123,
            'f2': dt1.isoformat(),
            'f3': dt2.isoformat(),
            'f4': 123,
            'f5': 2,
            'f6': 1,
            'f7': 2
        }, {'f1': 'x1', 'f2': 'x2.0', 'f3': 'x2.1', 'f4': 'x3.0', 'f5': 'x3.1', 'f6': 'x4.a', 'f7': 'x4.b'})
        self.assertDictEqual(d.value, {
            'x1': 123.0,
            'x2': [dt1, dt2],
            'x3': [123, 'z2'],
            'x4': {'a': 1, 'b': 2}
        })
        self.assertDictEqual(d.query, {
            '$set': {
                'x1': 123.0,
                'x2': [dt1, dt2],
                'x3': [123, 'z2'],
                'x4.a': 1,
                'x4.b': 2
            }
        })
        d.dirty_clear()
        self.assertFalse(d.dirty)
        self.assertEqual(d.query, {})

        self.assertEqual(125.0, d.prop1)
        self.assertEqual(246.0, d.prop2)
        self.assertIsNone(d._id)

    def test_document_2(self):
        from tests.util import Document2

        d = Document2()
        self.assertDictEqual(d.value, {
            'f1': [None, None],
            'f2': {'a': None, 'b': None},
            'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
            'm2': [],
            'd2': [],
            'd1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}}
        })

        dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
        dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)

        d.set({
            'f1': [111, 'x'],
            'f2': {'a': 222, 'b': None},
        })
        self.assertDictEqual(d.value, {
            'f1': [111, 'x'],
            'f2': {'a': 222, 'b': None},
            'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
            'm2': [],
            'd1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
            'd2': []
        })
        self.assertDictEqual(d.query, {'$set': {
            'f1': [111, 'x'],
            'f2.a': 222
        }})
        d['m1'] = {'x1': 1, 'x2': [dt1], 'x3': [2, None], 'x4': {'a': 3, 'b': None}}
        self.assertDictEqual(d.query, {'$set': {
            'f1': [111, 'x'],
            'f2.a': 222,
            'm1.x1': 1.0,
            'm1.x2': [dt1],
            'm1.x3': [2, None],
            'm1.x4.a': 3
        }})

        d['m2'].append({'x1': 1, 'x2': [dt1], 'x3': [2, None], 'x4': {'a': 3, 'b': None}})
        self.assertDictEqual(d.query, {'$set': {
            'f1': [111, 'x'],
            'f2.a': 222,
            'm1.x1': 1.0,
            'm1.x2': [dt1],
            'm1.x3': [2, None],
            'm1.x4.a': 3,
            'm2': [{
                'x2': [dt1],
                'x3': [2, None],
                'x1': 1.0,
                'x4': {'a': 3, 'b': None}}]
        }})

        d['m1.x2'] = [dt2, dt1]
        self.assertDictEqual(d.query, {'$set': {
            'f1': [111, 'x'],
            'f2.a': 222,
            'm1.x1': 1.0,
            'm1.x2': [dt2, dt1],
            'm1.x3': [2, None],
            'm1.x4.a': 3,
            'm2': [{
                'x2': [dt1],
                'x3': [2, None],
                'x1': 1.0,
                'x4': {'a': 3, 'b': None}}]
        }})

        self.assertEqual(d['m1'].prop1, 3.0)
        self.assertEqual(d['m2.0'].prop1, 3.0)
        d['m1.x1'] = 10
        d['m2.0.x1'] = 20
        self.assertEqual(d['m1'].prop1, 12.0)
        self.assertEqual(d['m2.0'].prop1, 22.0)

    def test_document_3(self):
        from tests.util import Document1, Document2
        dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)

        d = Document2()

        d['d1'] = {'x1': 100, 'x2': [dt2], 'x3': (200, 3), 'x4': {'b': 300}}
        self.assertTrue(d.dirty)
        self.assertDictEqual(d.value, {
            'f1': [None, None],
            'f2': {'a': None, 'b': None},
            'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
            'm2': [],
            'd1': {'x1': 100.0, 'x2': [dt2], 'x3': [200, 'z3'], 'x4': {'a': None, 'b': 300}},
            'd2': []
        })

        with self.assertRaises(mokito.errors.MokitoDBREFError):
            _ = d.query

        id1 = ObjectId()
        d['d1']._id = id1

        with self.assertRaises(mokito.errors.MokitoDBREFError):
            _ = d.query

        d['d1'].dirty_clear()
        self.assertDictEqual(d.query, {'$set': {'d1': DBRef(Document1.__collection__, id1)}})

        d.dirty_clear()
        self.assertEqual(d.query, {})

        d['d1.x4.a'] = 400
        with self.assertRaises(mokito.errors.MokitoDBREFError):
            _ = d.query

        d['d1'].dirty_clear()
        self.assertFalse(d.dirty)
        self.assertEqual(d.query, {})
        d['d1.x4.a'] = 500
        with self.assertRaises(mokito.errors.MokitoDBREFError):
            _ = d.query

        d.dirty_clear()
        self.assertEqual(d.query, {})

        self.assertEqual(d['d1'].prop1, 102.0)
        self.assertEqual(d['d1'].prop2, 200.0)

        d['d1'] = None
        self.assertDictEqual(d.query, {'$unset': {'d1': ''}})

    def test_document_4(self):
        from tests.util import Document1, Document2
        dt1 = datetime.datetime(2016, 1, 2, 3, 4, 5)
        dt2 = datetime.datetime(2016, 2, 3, 4, 5, 6)
        id1 = ObjectId()
        id2 = ObjectId()

        d = Document2()

        d['d2'].append({'x1': 100, 'x2': [dt1], 'x3': (200, 1), 'x4': {'b': 300}})
        self.assertTrue(d.dirty)
        self.assertDictEqual(d.value, {
            'f1': [None, None],
            'f2': {'a': None, 'b': None},
            'm1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
            'm2': [],
            'd1': {'x1': None, 'x2': [], 'x3': [None, None], 'x4': {'a': None, 'b': None}},
            'd2': [{'x1': 100.0, 'x2': [dt1], 'x3': [200, 'z1'], 'x4': {'a': None, 'b': 300}}],
        })

        with self.assertRaises(mokito.errors.MokitoDBREFError):
            _ = d.query

        d['d2.0']._id = id1
        d['d2.0'].dirty_clear()
        self.assertTrue(d.dirty)
        self.assertDictEqual(d.query, {'$set': {'d2': [DBRef(Document1.__collection__, id1)]}})

        d.dirty_clear()
        d['d2'][1] = {'x1': 200.0, 'x2': [dt2], 'x3': [300, 2], 'x4': {'a': None, 'b': 400}}
        with self.assertRaises(mokito.errors.MokitoDBREFError):
            _ = d.query

        d['d2.1']._id = id2
        d['d2.1'].dirty_clear()
        self.assertTrue(d.dirty)
        self.assertDictEqual(d.query, {'$set': {'d2': [DBRef(Document1.__collection__, id1),
                                                       DBRef(Document1.__collection__, id2)]}})
        del d['d2.0']
        self.assertDictEqual(d.query, {'$set': {'d2': [DBRef(Document1.__collection__, id2)]}})

        d.dirty_clear()
        d['d2.0.x1'] = 55
        with self.assertRaises(mokito.errors.MokitoDBREFError):
            _ = d.query

        self.assertDictEqual(d['d2'].value[0], {'x2': [dt2], 'x3': [300, 'z2'], 'x1': 55.0, 'x4': {'a': None, 'b': 400}})

    def test_model_choices(self):
        from mokito.fields import ChoiceField
        ch1 = ['foo', 'bar']
        ch2 = {'x': 1, 'y': 2}
        ch3 = {'a': 100, 'b': 200}

        class Model_0(mokito.Model):
            fields = {
                'd1': ChoiceField(ch1),
                'd2': [ChoiceField(ch2)],
                'd3': (int, ChoiceField(ch3)),
                'd4': {
                    'dd1': ChoiceField(ch1),
                    'dd2': [ChoiceField(ch2)],
                    'dd3': (int, ChoiceField(ch3))
                }
            }

        f = Model_0()
        f['d1'] = 'foo'
        f['d2'].append(1)
        f['d3.1'] = 100
        f['d4.dd1'] = 'foo'
        f['d4.dd2'].append(1)
        f['d4.dd3.1'] = 100
        self.assertDictEqual(f.value, {
            'd1': 'foo',
            'd2': ['x'],
            'd3': [None, 'a'],
            'd4': {
                'dd1': 'foo',
                'dd2': ['x'],
                'dd3': [None, 'a']
            }
        })

        f.set({
            'd1': 'bar',
            'd2': [2],
            'd3': [None, 200],
            'd4': {
                'dd1': 'bar',
                'dd2': [2],
                'dd3': [None, 200]
            }
        })
        self.assertDictEqual(f.value, {
            'd1': 'bar',
            'd2': ['y'],
            'd3': [None, 'b'],
            'd4': {
                'dd1': 'bar',
                'dd2': ['y'],
                'dd3': [None, 'b']
            }
        })

        f.clear()
        f.set({
            'd1': 'foo',
            'd2': ['x'],
            'd3': [None, 'a'],
            'd4': {
                'dd1': 'foo',
                'dd2': ['x'],
                'dd3': [None, 'a']
            }
        }, inner=True)
        self.assertDictEqual(f.value, {
            'd1': 'foo',
            'd2': ['x'],
            'd3': [None, 'a'],
            'd4': {
                'dd1': 'foo',
                'dd2': ['x'],
                'dd3': [None, 'a']
            }
        })
