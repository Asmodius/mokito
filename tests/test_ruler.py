# coding: utf-8

import sys
import datetime
import unittest
import random
import string
import copy

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

    def setUp(self):
        self.dict_rules = {
            'f_6': dict
            # 'f_6': {'f_6_1': int, 'f_6_2': str, 'f_6_3': {}, 'f_6_4': {}},
            # 'f_7': [None],
            # 'f_8': [str],
            # 'f_9': [{'f_9_1': int, 'f_9_2': str, 'f_9_3': {}}],
            # 'f_10': (int, str),
        }

    def test_Node_ObjectId(self):
        node1 = Node(ObjectId)
        node2 = Node(ObjectId)
        self.assertIsNotNone(node1)
        self.assertIsNotNone(node2)
        self.assertIsNone(node1.value())
        self.assertIsNone(node2.value())

        _id = ObjectId()
        node1.set(_id)
        self.assertEqual(node1.value(), _id)
        self.assertEqual(str(node1), str(_id))
        self.assertTrue(node1.changed)

        self.assertFalse(node1 == node2)
        node2.set(str(_id))
        self.assertTrue(node1 == node2)

        node1.clear()
        self.assertIsNone(node1.value())
        self.assertFalse(node1.changed)

    def test_Node_None(self):
        node = Node(None)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())

        node.set(None)
        self.assertIsNone(node.value())
        self.assertFalse(node.changed)

        for x in (random_int(), random_str(), random_float(), random_datetime()):
            node.set(x)
            self.assertEqual(node.value(), x)
            self.assertTrue(node.changed)

    def test_Node_str(self):
        node = Node(str)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())

        x = random_str()
        node.set(x)
        self.assertEqual(node.value(), x)
        self.assertTrue(node.changed)

        x = random_int()
        node.set(x)
        self.assertEqual(node.value(), str(x))
        self.assertTrue(node.changed)

    def test_Node_int(self):
        node1 = Node(int)
        self.assertIsNotNone(node1)
        self.assertIsNone(node1.value())
        node2 = Node(int)
        self.assertIsNotNone(node2)
        self.assertIsNone(node2.value())

        x1 = random_int()
        node1.set(x1)
        self.assertEqual(node1.value(), x1)
        self.assertTrue(node1.changed)
        x2 = random_int()
        node2.set(x2)
        self.assertEqual(node2.value(), x2)
        self.assertTrue(node2.changed)

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

    def test_Node_bool(self):
        node = Node(bool)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())

        node.set(True)
        self.assertTrue(node.value())
        node.set(False)
        self.assertFalse(node.value())
        node.set(1)
        self.assertEqual(node.value(), True)
        node.set('')
        self.assertEqual(node.value(), False)

    def test_Node_float(self):
        node1 = Node(float)
        self.assertIsNotNone(node1)
        self.assertIsNone(node1.value())
        node2 = Node(float)
        self.assertIsNotNone(node2)
        self.assertIsNone(node2.value())

        x1 = random_float()
        node1.set(x1)
        self.assertEqual(node1.value(), x1)
        self.assertTrue(node1.changed)
        x2 = random_float()
        node2.set(x2)
        self.assertEqual(node2.value(), x2)
        self.assertTrue(node2.changed)

        self.assertEqual(node1.value() == node2.value(), x1 == x2)
        self.assertEqual(node1 == node2, x1 == x2)
        self.assertEqual(node1 != node2, x1 != x2)
        self.assertEqual(node1 > node2, x1 > x2)
        self.assertEqual(node1 < node2, x1 < x2)
        self.assertTrue(node1 == x1)
        self.assertTrue(node2 == x2)

        with self.assertRaises(ValueError):
            node1.set('foo')

    def test_Node_datetime(self):
        node = Node(datetime.datetime)
        self.assertIsNotNone(node)
        self.assertIsNone(node.value())

        x = random_datetime()
        node.set(x)
        self.assertEqual(node.value(), x)

        with self.assertRaises(TypeError):
            node.set('foo')

    def test_Node_dict(self):
        x1 = {
            'f_1': 'bar',
            'f_2': {
                'a': 1,
                'b': .2
            },
            'f_3': [1, 'a', 3]
        }
        x2 = copy.copy(x1)

        node1 = NodeDict(dict)
        self.assertIsNotNone(node1)
        self.assertEqual(node1.value(), {})
        node2 = NodeDict(dict)
        self.assertIsNotNone(node2)
        self.assertEqual(node2.value(), {})

        node1.set(x1)
        node2.set(x1)
        self.assertDictEqual(node1.value(), x1)
        self.assertListEqual(sorted(node1.changed), sorted(x1.keys()))
        self.assertTrue(node1 == x1)
        self.assertTrue(node1 == node2)

        node1.changed_clear()
        self.assertDictEqual(node1.value(), x1)
        self.assertEqual(node1.changed, [])

        self.assertEqual(node1['f_1'], 'bar')
        x2['f_1'] = 100
        node1['f_1'] = 100
        self.assertDictEqual(node1.value(), x2)
        self.assertEqual(node1.changed, ['f_1'])
        self.assertFalse(node1 == node2)
        self.assertEqual(node1['f_1'], 100)

        x2['f_3'][1] = 100
        node1['f_3'][1] = 100
        self.assertDictEqual(node1.value(), x2)
        self.assertEqual(sorted(node1.changed), ['f_1', 'f_3'])
        self.assertEqual(node1['f_3'][1], 100)

        # x2['f_3'][2] = 200
        # node1['f_3.2'] = 200
        # self.assertDictEqual(node1.value(), x2)
        # self.assertEqual(sorted(node1.changed), ['f_1', 'f_3'])
        # self.assertEqual(node1['f_3.2'], 200)
        #
        # print node1.changed
        # print node1.value()



