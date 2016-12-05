
x = {
    'a': 1,
    'b': [2, 3],
    'c': {
        'x': 4,
        'y': [5, 6]
    }
}

# x = {
#     'a': 1,
#     'b.0': 2,
#     'b.1': 3,
#     'c.x': 4,
#     'c.y.0': 5
#     'c.y.1': 6
# }


def obj_to_dot(obj, prefix=None):
    if isinstance(obj, list):
        obj = {k: v for k, v in enumerate(obj)}

    if isinstance(obj, dict):
        res = {}
        for k, v in obj.items():
            res.update(obj_to_dot(v, '%s.%s' % (prefix, k) if prefix else k))
        return res

    return {prefix: obj}

print
y = obj_to_dot(x)
z = y.keys()
z.sort()
for i in z:
    print "%s:%s" % (i, y[i])



# class Document1(mokito.Document):
#     __collection__ = 'TEST_COLLECTION1'
#     __model__ = {
#         'x1': float,
#         'x2': [datetime.datetime],
#         'x3': (int, str),
#         'x4': {'a': int, 'b': int}
#     }
#
#
# class Document2(mokito.Document):
#     __collection__ = 'TEST_COLLECTION2'
#     __model__ = {
#         'x3': (int, str),
#         'x4': {'a': int, 'b': int},
#
#         'm1': {
#             'x1': float,
#             'x2': [datetime.datetime],
#             'x3': (int, str),
#             'x4': {'a': int, 'b': int}
#         },
#         'm2': [{
#             'x1': float,
#             'x2': [datetime.datetime],
#             'x3': (int, str),
#             'x4': {'a': int, 'b': int}
#         }],
#
#         'd1': Document1,
#         'd2': [Document1]
#     }
