# import unittest
#
# from mokito.tools import make_field
# from mokito.geo_fileds import (
#     GEOPointField,
#     GEOLineField,
#     GEOPolygonField,
#     GEOMultiPointField,
#     GEOMultiLineField
# )
# from mokito.models import Model
# from mokito.documents import Document
#
#
# class TestGeoFields(unittest.TestCase):
#     def test_point_field_1(self):
#         f = make_field(GEOPointField)
#         self.assertIsInstance(f, GEOPointField)
#         self.assertDictEqual(f.value, {
#             'type': 'Point',
#             'coordinates': [None, None]
#         })
#         self.assertDictEqual(f.query, {})
#         f['coordinates'].value = [-1, -2]
#         self.assertDictEqual(f.value, {
#             'type': 'Point',
#             'coordinates': [-1.0, -2.0]
#         })
#         self.assertEqual(f['coordinates.1'].value, -2.0)
#         f['coordinates.1'].value = 3.0
#         self.assertDictEqual(f.value, {
#             'type': 'Point',
#             'coordinates': [-1.0, 3.0]
#         })
#         with self.assertRaises(IndexError):
#             f['coordinates.3'].value = 4.0
#
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'Point',
#             'coordinates': [-1.0, 3.0]}
#         })
#
#     def test_point_field_2(self):
#         f = make_field(GEOPointField([123, 45]))
#         self.assertIsInstance(f, GEOPointField)
#         self.assertDictEqual(f.value, {
#             'type': 'Point',
#             'coordinates': [123.0, 45.0]
#         })
#         self.assertDictEqual(f.query, {})
#         f['coordinates'].value = [-1, -2]
#         self.assertDictEqual(f.value, {
#             'type': 'Point',
#             'coordinates': [-1.0, -2.0]
#         })
#         self.assertEqual(f['coordinates.1'].value, -2.0)
#         f['coordinates.1'].value = 3.0
#         self.assertDictEqual(f.value, {
#             'type': 'Point',
#             'coordinates': [-1.0, 3.0]
#         })
#         with self.assertRaises(IndexError):
#             f['coordinates.3'].value = 4.0
#
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'Point',
#             'coordinates': [-1.0, 3.0]}
#         })
#
#     def test_line_field_1(self):
#         f = make_field(GEOLineField)
#         self.assertIsInstance(f, GEOLineField)
#         self.assertDictEqual(f.value, {
#             'type': 'LineString',
#             'coordinates': []
#         })
#         self.assertDictEqual(f.query, {})
#
#         f['coordinates.0'].value = [-1, -2]
#         self.assertDictEqual(f.value, {
#             'type': 'LineString',
#             'coordinates': [[-1.0, -2.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'LineString',
#             'coordinates': [[-1.0, -2.0]]
#         }})
#
#         f['coordinates'].append_value([3, 4])
#         self.assertDictEqual(f.value, {
#             'type': 'LineString',
#             'coordinates': [[-1.0, -2.0], [3.0, 4.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'LineString',
#             'coordinates': [[-1.0, -2.0], [3.0, 4.0]]
#         }})
#         self.assertEqual(f['coordinates.0.1'].value, -2.0)
#
#         f['coordinates.0.1'].value = 3.0
#         self.assertDictEqual(f.value, {
#             'type': 'LineString',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'LineString',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0]]
#         }})
#
#         f['coordinates.3.1'].value = 4.0
#         self.assertDictEqual(f.value, {
#             'type': 'LineString',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'LineString',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0]]
#         }})
#
#         with self.assertRaises(IndexError):
#             f['coordinates.3.4'].value = 5.0
#
#     def test_line_field_2(self):
#         f = make_field(GEOLineField([[1.23, 4.5]]))
#         self.assertIsInstance(f, GEOLineField)
#         self.assertDictEqual(f.value, {
#             'type': 'LineString',
#             'coordinates': [[1.23, 4.5]]
#         })
#         self.assertDictEqual(f.query, {})
#
#         f['coordinates.0'].value = [-1, -2]
#         self.assertDictEqual(f.value, {
#             'type': 'LineString',
#             'coordinates': [[-1.0, -2.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'LineString',
#             'coordinates': [[-1.0, -2.0]]
#         }})
#
#         f['coordinates'].append_value([3, 4])
#         self.assertDictEqual(f.value, {
#             'type': 'LineString',
#             'coordinates': [[-1.0, -2.0], [3.0, 4.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'LineString',
#             'coordinates': [[-1.0, -2.0], [3.0, 4.0]]
#         }})
#         self.assertEqual(f['coordinates.0.1'].value, -2.0)
#
#         f['coordinates.0.1'].value = 3.0
#         self.assertDictEqual(f.value, {
#             'type': 'LineString',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'LineString',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0]]
#         }})
#
#         f['coordinates.3.1'].value = 4.0
#         self.assertDictEqual(f.value, {
#             'type': 'LineString',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0], [1.23, 4.5], [1.23, 4.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'LineString',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0], [1.23, 4.5], [1.23, 4.0]]
#         }})
#
#         with self.assertRaises(IndexError):
#             f['coordinates.3.4'].value = 5.0
#
#     def test_polygon_field_1(self):
#         f = make_field(GEOPolygonField)
#         self.assertIsInstance(f, GEOPolygonField)
#         self.assertDictEqual(f.value, {
#             'type': 'Polygon',
#             'coordinates': []
#         })
#         self.assertDictEqual(f.query, {})
#
#         f['coordinates.0.0'].value = [-1, -2]
#         self.assertDictEqual(f.value, {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, -2.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, -2.0]]
#             ]
#         }})
#
#         f['coordinates.0'].append_value([3, 4])
#         self.assertDictEqual(f.value, {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, -2.0], [3.0, 4.0], [-1.0, -2.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, -2.0], [3.0, 4.0], [-1.0, -2.0]]
#             ]
#         }})
#         self.assertEqual(f['coordinates.0.0.1'].value, -2.0)
#
#         f['coordinates.0.0.1'].value = 3.0
#
#         self.assertDictEqual(f.value, {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [-1.0, 3.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [-1.0, 3.0]]
#             ]
#         }})
#
#         f['coordinates.0.3.1'].value = 4.0
#
#         self.assertDictEqual(f.value, {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0], [-1.0, 3.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0], [-1.0, 3.0]]
#             ]
#         }})
#
#         with self.assertRaises(IndexError):
#             f['coordinates.0.3.4'].value = 5.0
#
#         f['coordinates.0'].append_value([5, 6.0])
#         self.assertDictEqual(f.value, {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0], [5.0, 6.0], [-1.0, 3.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0], [5.0, 6.0], [-1.0, 3.0]]
#             ]
#         }})
#
#         f['coordinates.1'].append_value([7, 8.0])
#         f['coordinates.1.1'].value = [9, 10.0]
#         self.assertDictEqual(f.value, {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0], [5.0, 6.0], [-1.0, 3.0]],
#                 [[7.0, 8.0], [9.0, 10.0], [7.0, 8.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'Polygon',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0], [5.0, 6.0], [-1.0, 3.0]],
#                 [[7.0, 8.0], [9.0, 10.0], [7.0, 8.0]]
#             ]
#         }})
#
#     def test_multi_point_field_1(self):
#         f = make_field(GEOMultiPointField)
#         self.assertIsInstance(f, GEOMultiPointField)
#         self.assertDictEqual(f.value, {
#             'type': 'MultiPoint',
#             'coordinates': []
#         })
#         self.assertDictEqual(f.query, {})
#
#         f['coordinates.0'].value = [-1, -2]
#         self.assertDictEqual(f.value, {
#             'type': 'MultiPoint',
#             'coordinates': [[-1.0, -2.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'MultiPoint',
#             'coordinates': [[-1.0, -2.0]]
#         }})
#
#         f['coordinates'].append_value([3, 4])
#         self.assertDictEqual(f.value, {
#             'type': 'MultiPoint',
#             'coordinates': [[-1.0, -2.0], [3.0, 4.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'MultiPoint',
#             'coordinates': [[-1.0, -2.0], [3.0, 4.0]]
#         }})
#         self.assertEqual(f['coordinates.0.1'].value, -2.0)
#
#         f['coordinates.0.1'].value = 3.0
#         self.assertDictEqual(f.value, {
#             'type': 'MultiPoint',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'MultiPoint',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0]]
#         }})
#
#         f['coordinates.3.1'].value = 4.0
#         self.assertDictEqual(f.value, {
#             'type': 'MultiPoint',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0]]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'MultiPoint',
#             'coordinates': [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0]]
#         }})
#
#         with self.assertRaises(IndexError):
#             f['coordinates.3.4'].value = 5.0
#
#     def test_multi_line_field_1(self):
#         f = make_field(GEOMultiLineField)
#         self.assertIsInstance(f, GEOMultiLineField)
#         self.assertDictEqual(f.value, {
#             'type': 'MultiLineString',
#             'coordinates': []
#         })
#         self.assertDictEqual(f.query, {})
#
#         f['coordinates.0.0'].value = [-1, -2]
#         self.assertDictEqual(f.value, {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, -2.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, -2.0]]
#             ]
#         }})
#
#         f['coordinates.0'].append_value([3, 4])
#         self.assertDictEqual(f.value, {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, -2.0], [3.0, 4.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, -2.0], [3.0, 4.0]]
#             ]
#         }})
#         self.assertEqual(f['coordinates.0.0.1'].value, -2.0)
#
#         f['coordinates.0.0.1'].value = 3.0
#
#         self.assertDictEqual(f.value, {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0]]
#             ]
#         }})
#
#         f['coordinates.0.3.1'].value = 4.0
#
#         self.assertDictEqual(f.value, {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0]]
#             ]
#         }})
#
#         with self.assertRaises(IndexError):
#             f['coordinates.0.3.4'].value = 5.0
#
#         f['coordinates.0'].append_value([5, 6.0])
#         self.assertDictEqual(f.value, {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0], [5.0, 6.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0], [5.0, 6.0]]
#             ]
#         }})
#
#         f['coordinates.1'].append_value([7, 8.0])
#         f['coordinates.1.1'].value = [9, 10.0]
#         self.assertDictEqual(f.value, {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0], [5.0, 6.0]],
#                 [[7.0, 8.0], [9.0, 10.0]]
#             ]
#         })
#         self.assertDictEqual(f.query, {'$set': {
#             'type': 'MultiLineString',
#             'coordinates': [
#                 [[-1.0, 3.0], [3.0, 4.0], [None, None], [None, 4.0], [5.0, 6.0]],
#                 [[7.0, 8.0], [9.0, 10.0]]
#             ]
#         }})
#
#     def test_type_1(self):
#         f = make_field(GEOPointField)
#         self.assertEqual(f['type'].value, 'Point')
#         f['type'].value = 'foo'
#         self.assertEqual(f['type'].value, 'Point')
#
#     def test_set_line_field_1(self):
#         f1 = make_field(GEOLineField)
#         f2 = make_field(GEOLineField)
#         f1['coordinates.0'].value = [-1, -2]
#         f2['coordinates.0'] = f1['coordinates.0']
#         self.assertDictEqual(f2.value, {
#             'type': 'LineString',
#             'coordinates': [[-1.0, -2.0]]
#         })
#         self.assertDictEqual(f2.query, {'$set': {
#             'type': 'LineString',
#             'coordinates': [[-1.0, -2.0]]
#         }})
#
#     def test_set_polygon_field_1(self):
#         f1 = make_field(GEOPolygonField)
#         f2 = make_field(GEOPolygonField)
#         f1['coordinates.0'].value = [[-1, -2], [3, 4]]
#         f2['coordinates.0'] = f1['coordinates.0']
#         self.assertDictEqual(f2.value, {
#             'type': 'Polygon',
#             'coordinates': [[[-1.0, -2.0], [3.0, 4.0], [-1.0, -2.0]]]
#         })
#         self.assertDictEqual(f2.query, {'$set': {
#             'type': 'Polygon',
#             'coordinates': [[[-1.0, -2.0], [3.0, 4.0], [-1.0, -2.0]]]
#         }})
#
#     def test_model(self):
#         class GeoModel(Model):
#             scheme = {
#                 'a': GEOPointField([1.2, -3.4])
#             }
#
#         class GeoDocument(Document):
#             __collection__ = 'geo'
#             scheme = {
#                 'foo': GeoModel,
#                 'bar': GEOPolygonField
#             }
#
#         f = GeoDocument()
#         self.assertDictEqual(f.value, {
#             '_id': None,
#             'foo': {
#                 'a': {
#                     'type': 'Point',
#                     'coordinates': [1.2, -3.4]
#                 }
#             },
#             'bar': {
#                 'type': 'Polygon',
#                 'coordinates': []
#             }
#         })
#
#         f['foo.a.coordinates.1'].value = 5
#         f['bar.coordinates.0'].value = [[5, 6], [7, 8]]
#         self.assertDictEqual(f.value, {
#             '_id': None,
#             'foo': {
#                 'a': {
#                     'type': 'Point',
#                     'coordinates': [1.2, 5.0]
#                 }
#             },
#             'bar': {
#                 'type': 'Polygon',
#                 'coordinates': [
#                     [[5.0, 6.0], [7.0, 8.0], [5.0, 6.0]]
#                 ]
#             }
#         })
