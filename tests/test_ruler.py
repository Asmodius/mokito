# coding: utf-8

import sys
import datetime
import unittest
import random
import string

from bson import ObjectId

from mokito.ruler import *


def random_int():
    return random.randint(-sys.maxint, sys.maxint)


def random_float():
    return random.uniform(-sys.maxint, sys.maxint)


def random_str(n=100):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))


def random_datetime():
    return datetime.datetime(random.randint(2000, 2100),
                             random.randint(1, 12),
                             random.randint(1, 28),
                             random.randint(0, 23),
                             random.randint(0, 59),
                             random.randint(0, 59))


class TestSequenceFunctions(unittest.TestCase):

    def test_Node_ObjectId(self):
        node1 = Node(ObjectId)
        self.assertIsNotNone(node1)
        self.assertIsNone(node1.value())
        self.assertFalse(node1.dirty)
        node2 = Node(ObjectId)
        self.assertIsNotNone(node2)
        self.assertIsNone(node2.value())
        self.assertFalse(node2.dirty)

        _id = ObjectId()
        node1.set(_id)
        self.assertEqual(node1.value(), _id)
        self.assertEqual(str(node1), str(_id))
        self.assertTrue(node1.dirty)

        self.assertFalse(node1 == node2)
        node2.set(str(_id))
        self.assertTrue(node1 == node2)

        node1.clear()
        self.assertIsNone(node1.value())
        self.assertFalse(node1.dirty)

    def test_Node_None(self):
        node = Node(None)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())
        self.assertFalse(node.dirty)

        node.set(None)
        self.assertIsNone(node.value())
        self.assertFalse(node.dirty)

        for x in (random_int(), random_str(), random_float(), random_datetime()):
            node.set(x)
            self.assertEqual(node.value(), x)
            self.assertTrue(node.dirty)

    def test_Node_str_1(self):
        node = Node(str)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())
        self.assertFalse(node.dirty)

        x = random_str()
        node.set(x)
        self.assertEqual(node.value(), x)
        self.assertTrue(node.dirty)

        x = random_int()
        node.set(x)
        self.assertEqual(node.value(), str(x))
        self.assertTrue(node.dirty)

    def test_Node_str_2(self):
        node = Node(str)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())
        self.assertFalse(node.dirty)

        x = random_str()
        node.set(x)
        node.changed_clear()
        self.assertFalse(node.dirty)
        node.set(x)
        self.assertFalse(node.dirty)
        self.assertEqual(node.value(), x)

    def test_Node_int_1(self):
        node1 = Node(int)
        self.assertIsNotNone(node1)
        self.assertIsNone(node1.value())
        self.assertFalse(node1.dirty)
        node2 = Node(int)
        self.assertIsNotNone(node2)
        self.assertIsNone(node2.value())
        self.assertFalse(node2.dirty)

        x1 = random_int()
        node1.set(x1)
        self.assertEqual(node1.value(), x1)
        self.assertTrue(node1.dirty)
        x2 = random_int()
        node2.set(x2)
        self.assertEqual(node2.value(), x2)
        self.assertTrue(node2.dirty)

        self.assertEqual(node1.value() == node2.value(), x1 == x2)
        self.assertEqual(node1 == node2, x1 == x2)
        self.assertEqual(node1 != node2, x1 != x2)
        self.assertEqual(node1 > node2, x1 > x2)
        self.assertEqual(node1 < node2, x1 < x2)
        self.assertTrue(node1 == x1)
        self.assertTrue(node2 == x2)

        x1 = random_int()
        node1.set(str(x1))
        self.assertEqual(node1.value(), x1)

        with self.assertRaises(ValueError):
            node1.set('foo')

    def test_Node_int_2(self):
        node = Node(int)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())
        self.assertFalse(node.dirty)

        x = random_int()
        node.set(x)
        self.assertTrue(node.dirty)
        node.changed_clear()
        node.set(x)
        self.assertFalse(node.dirty)
        self.assertEqual(node.value(), x)

    def test_Node_bool_1(self):
        node = Node(bool)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())
        self.assertFalse(node.dirty)

        node.set(True)
        self.assertTrue(node.value())
        self.assertTrue(node.dirty)
        node.set(False)
        self.assertFalse(node.value())
        self.assertTrue(node.dirty)
        node.set(1)
        self.assertTrue(node.value())
        self.assertTrue(node.dirty)
        node.set('')
        self.assertFalse(node.value())
        self.assertTrue(node.dirty)

    def test_Node_bool_2(self):
        node = Node(bool)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())
        self.assertFalse(node.dirty)

        node.set(True)
        self.assertTrue(node.value())
        self.assertTrue(node.dirty)
        node.changed_clear()
        node.set(True)
        self.assertTrue(node.value())
        self.assertFalse(node.dirty)

    def test_Node_float_1(self):
        node1 = Node(float)
        self.assertIsNotNone(node1)
        self.assertIsNone(node1.value())
        self.assertFalse(node1.dirty)
        node2 = Node(float)
        self.assertIsNotNone(node2)
        self.assertIsNone(node2.value())
        self.assertFalse(node2.dirty)

        x1 = random_float()
        node1.set(x1)
        self.assertEqual(node1.value(), x1)
        self.assertTrue(node1.dirty)
        x2 = random_float()
        node2.set(x2)
        self.assertEqual(node2.value(), x2)
        self.assertTrue(node2.dirty)

        self.assertEqual(node1.value() == node2.value(), x1 == x2)
        self.assertEqual(node1 == node2, x1 == x2)
        self.assertEqual(node1 != node2, x1 != x2)
        self.assertEqual(node1 > node2, x1 > x2)
        self.assertEqual(node1 < node2, x1 < x2)
        self.assertTrue(node1 == x1)
        self.assertTrue(node2 == x2)

        with self.assertRaises(ValueError):
            node1.set('foo')

    def test_Node_float_2(self):
        node = Node(float)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())
        self.assertFalse(node.dirty)

        x = random_float()
        node.set(x)
        self.assertTrue(node.dirty)
        node.changed_clear()
        node.set(x)
        self.assertFalse(node.dirty)
        self.assertEqual(node.value(), x)

    def test_Node_datetime(self):
        node = Node(datetime.datetime)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())

        x = random_datetime()
        node.set(x)
        self.assertEqual(node.value(), x)
        self.assertTrue(node.dirty)
        node.changed_clear()
        node.set(x)
        self.assertFalse(node.dirty)
        self.assertEqual(node.value(), x)

        with self.assertRaises(TypeError):
            node.set('foo')

    def test_NodeTuple_1(self):
        node = NodeTuple(tuple)
        self.assertIsNotNone(node)
        self.assertEqual(node.value(), [])
        node.set([1])
        self.assertEqual(node.value(), [])

    def test_NodeTuple_2(self):
        rul = (int,)
        node1 = NodeTuple(rul)
        self.assertIsNotNone(node1)
        self.assertEqual(node1.value(), [None])
        self.assertFalse(node1.dirty)
        node2 = NodeTuple(rul)
        self.assertIsNotNone(node2)
        self.assertEqual(node2.value(), [None])
        self.assertFalse(node2.dirty)

        x1 = random_int()
        x2 = random_int()
        node1.set([x1])
        self.assertEqual(node1.value(), [x1])
        self.assertTrue(node1.dirty)

        node1.set([x2, x1])
        self.assertEqual(node1.value(), [x2])

        with self.assertRaises(ValueError):
            node1.set(['foo'])
        self.assertEqual(node1.value(), [x2])

        x2 = random_int()
        node1[0] = x2
        self.assertEqual(node1.value(), [x2])

        self.assertFalse(node1 == node2)
        node2.set((x2,))
        self.assertTrue(node1 == node2)

        self.assertTrue(x2 in node1)

        with self.assertRaises(IndexError):
            del node1[1]
        self.assertEqual(node1.value(), [x2])

        del node1[0]
        self.assertEqual(node1.value(), [None])

        with self.assertRaises(IndexError):
            node1.insert(1, x1)
        self.assertEqual(node1.value(), [None])

        node1.insert(0, x1)
        self.assertEqual(node1.value(), [x1])

    def test_NodeTuple_3(self):
        rul = (int, str,)
        node = NodeTuple(rul)
        self.assertIsNotNone(node)
        self.assertEqual(node.value(), [None, None])
        self.assertFalse(node.dirty)

        x1 = random_int()
        x2 = random_int()
        s2 = str(x2)
        node.set([x1, x2])
        self.assertEqual(node.value(), [x1, s2])
        self.assertEqual(node[0], x1)
        self.assertEqual(node[1], s2)
        del node[1]
        self.assertEqual(node.value(), [x1, None])
        self.assertTrue(node.dirty)

    def test_NodeTuple_4(self):
        rul = (None, dict, list, (int, str,))
        node = NodeTuple(rul)
        self.assertIsNotNone(node)
        self.assertEqual(node.value(), [None, {}, [], [None, None]])
        self.assertFalse(node.dirty)

        x1 = random_int()
        x2 = random_int()
        x3 = random_str()
        data = [
            x3,
            {'x1': x1, 'x2': x3},
            [x1, x3],
            (x1, x3,)
        ]
        node.set(data)
        data[3] = list(data[3])
        self.assertEqual(node[0], data[0])
        self.assertDictEqual(node[1].value(), data[1])
        self.assertEqual(node[2].value(), data[2])
        self.assertEqual(node[3].value(), data[3])

        self.assertEqual(node[2][0], data[2][0])
        self.assertEqual(node['2.0'], data[2][0])
        self.assertEqual(node[1]['x2'], data[1]['x2'])
        self.assertEqual(node['1.x2'], data[1]['x2'])

        data[2][0] = x2
        node[2][0] = x2
        self.assertEqual(node[2], data[2])
        data[2][0] = x1
        node['2.0'] = x1
        self.assertEqual(node[2], data[2])

        del node[0]
        data[0] = None
        self.assertEqual(node[0], data[0])

        del node[1]
        data[1] = {}
        self.assertEqual(node.value(), data)

        self.assertEqual(node[2:3], data[2:3])
        self.assertEqual(node[:2], data[:2])
        self.assertEqual(node[3:], data[3:])

        data[2] = []
        data[3] = [None, None]
        del node[2:]
        self.assertEqual(node.value(), data)

    def test_NodeList_1(self):
        node = NodeList(list)
        self.assertIsNotNone(node)
        self.assertEqual(node.value(), [])

        x1 = random_int()
        x2 = random_str()
        data = [x1]
        node.set([x1])
        self.assertEqual(node.value(), data)
        data.append(x2)
        node.append(x2)
        self.assertEqual(node.value(), data)

    def test_NodeList_2(self):
        rul = [(int, str,)]
        node = NodeList(rul)
        self.assertIsNotNone(node)
        print node.value()
        self.assertEqual(node.value(), [])
        self.assertFalse(node.dirty)

        x1 = random_int()
        s1 = random_str()
        x2 = random_int()
        s2 = random_int()
        x4 = random_int()
        data = [
            [x1, s1],
            [x2, s2],
        ]
        node.set(data)
        data[1][1] = str(data[1][1])
        self.assertEqual(node.value(), data)
        self.assertEqual(node[0].value(), data[0])
        self.assertEqual(node[1].value(), data[1])

        self.assertEqual(node[0][0], data[0][0])
        self.assertEqual(node['0.0'], data[0][0])

        data[0][0] = x4
        node[0][0] = x4
        self.assertEqual(node.value(), data)

        data[1][0] = x4
        node['1.0'] = x4
        self.assertEqual(node.value(), data)

        self.assertEqual(len(node), len(data))
        del data[1]
        del node[1]
        self.assertEqual(node.value(), data)
        self.assertEqual(len(node), len(data))

        data.append([x1, str(x1)])
        node.append([x1, x1])
        self.assertEqual(node.value(), data)
        self.assertEqual(len(node), len(data))

        self.assertEqual(node[0:], data[0:])
        self.assertEqual(node[:1], data[:1])
        self.assertEqual(node[:], data[:])

        del data[0:]
        del node[0:]
        self.assertEqual(node.value(), data)

    def test_Node_dict_1(self):
        data = {
            'x1': 'foo',
            'x2': {
                'y1': 123,
                'y2': .5
            },
            'x3': [321],
        }

        node1 = NodeDict(dict)
        self.assertIsNotNone(node1)
        self.assertEqual(node1.value(), {})
        node2 = NodeDict(dict)
        self.assertIsNotNone(node2)
        self.assertEqual(node2.value(), {})

        node1.set(data)
        node2.set(data)
        self.assertDictEqual(node1.value(), data)
        self.assertTrue(node1 == data)
        self.assertTrue(node1 == node2)

        node1.changed_clear()
        self.assertDictEqual(node1.value(), data)
        self.assertEqual(node1['x1'], 'foo')

        self.assertEqual(len(node1), 3)
        data['f_1'] = 100
        node1['f_1'] = 100

        self.assertDictEqual(node1.value(), data)
        self.assertFalse(node1 == node2)
        self.assertTrue(node1 != node2)
        self.assertEqual(node1['f_1'], 100)

        self.assertEqual(len(node1), 4)

    def test_Node_dict_2(self):
        rul = {
            'x1': str,
            'x2': {
                'y1': int,
                'y2': float
            },
            'x3': [int],
            'x4': (int, None)
        }

        node = NodeDict(rul)
        self.assertIsNotNone(node)
        self.assertDictEqual(node.value(),
                             {'x1': None,
                              'x2': {'y1': None, 'y2': None},
                              'x3': [],
                              'x4': [None, None]})
        data = {
            'x1': random_str(),
            'x2': {
                'y1': random_int(),
                'y2': random_float(),
            },
            'x3': [random_int()],
            'x4': (random_int(), random_datetime())
        }
        node.set(data)
        data['x4'] = list(data['x4'])
        self.assertDictEqual(node.value(), data)

        self.assertEqual(node['x2']['y1'], data['x2']['y1'])
        self.assertEqual(node['x2.y1'], data['x2']['y1'])
        self.assertEqual(node['x4.0'], data['x4'][0])

        with self.assertRaises(KeyError):
            node['f_1'] = 100

        del node['x1']
        data['x1'] = None
        self.assertDictEqual(node.value(), data)
