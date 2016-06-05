# coding: utf-8

import sys
import random
import string
import datetime


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
