from .fields import FloatField, StringField
from .collections import TupleField, ListField, DictField


class _ConstString(StringField):
    def __init__(self, _default=None, _parent=None, **kwargs):
        super().__init__(_default, _parent, **kwargs)
        self._val = self.validate(_default)

    def set_value(self, value, **kwargs):
        pass

    value = property(StringField.get_value, set_value)


class _Longitude(FloatField):
    def validate(self, value, **kwargs):
        if value is not None:
            value = float(value)
            if value < -180.0 or value > 180.0:
                raise ValueError()
        return value


class _Latitude(FloatField):
    def validate(self, value, **kwargs):
        if value is not None:
            value = float(value)
            if value < -90.0 or value > 90.0:
                raise ValueError()
        return value


class _Point1(TupleField):
    """
    [lng, lat]
    """

    def __init__(self, _default=None, _parent=None, **kwargs):
        if _default is None:
            _default = [None, None]

        rules = [_Longitude(_default=_default[0]),
                 _Latitude(_default=_default[1])]
        super().__init__(rules, _parent=_parent, **kwargs)

    def get_long(self):
        return self[0].value

    def set_long(self, value):
        self[0].value = value

    longitude = property(get_long, set_long)

    def get_lat(self):
        return self[1].value

    def set_lat(self, value):
        self[1].value = value

    latitude = property(get_lat, set_lat)


class _Point2(ListField):
    """
    [
        [lng, lat], ..., [lngN, latN]
    ]
    """

    def __init__(self, _default=None, _parent=None, **kwargs):
        if _default is None:
            rules = [_Point1()]
        else:
            rules = [_Point1(i) for i in _default]
        super().__init__(rules, _parent=_parent, **kwargs)

    def get_value(self, **kwargs):
        return [self._test_item(i).get_value(**kwargs) for i in map(str, range(len(self)))]

    value = property(get_value, ListField.set_value)


class _Point3(ListField):
    """
    [
        [ [lng1, lat1], ..., [lng1N, lat1N] ],
        ...
        [ [lngP, latP], ..., [lngPN, latPN] ]
    ]
    """

    def __init__(self, _default=None, _parent=None, **kwargs):
        if _default is None:
            rules = [_Point2()]
        else:
            rules = [_Point2(i) for i in _default]
        super().__init__(rules, _parent=_parent, **kwargs)

    def get_value(self, **kwargs):
        return [self._test_item(i).get_value(**kwargs) for i in map(str, range(len(self)))]

    value = property(get_value, ListField.set_value)


class _Point4(_Point3):
    """
    [
        [ [lng1, lat1], ..., [lng1N, lat1N] ],
        ...
        [ [lngP, latP], ..., [lngPN, latPN] ]
    ]
    """

    def get_value(self, **kwargs):
        ret = super().get_value(**kwargs)
        if ret:
            for k, v in enumerate(ret):
                if v and v[0] != v[-1]:
                    ret[k].append(v[0])
        return ret

    value = property(get_value, _Point3.set_value)


class _Point5(ListField):
    """
    [
        [
            [ [lng1, lat1], ..., [lng1N, lat1N] ],
            ...
            [ [lngP, latP], ..., [lngPN, latPN] ]
        ],
        ...
        [
            [ [lng1, lat1], ..., [lng1N, lat1N] ],
            ...
            [ [lngP, latP], ..., [lngPN, latPN] ]
        ]
    ]
    """

    def __init__(self, _default=None, _parent=None, **kwargs):
        if _default is None:
            rules = [_Point4()]
        else:
            rules = [_Point4(i) for i in _default]
        super().__init__(rules, _parent=_parent, **kwargs)

    def get_value(self, **kwargs):
        return [self._test_item(i).get_value(**kwargs) for i in map(str, range(len(self)))]

    value = property(get_value, ListField.set_value)


class GEOField(DictField):
    def make_query(self, short=False):
        if self.dirty:
            return True if short else {'$set': self.value}
        return {}

    query = property(make_query)


class GEOPointField(GEOField):
    def __init__(self, _default=None, _parent=None, **kwargs):
        rules = {
            'type': _ConstString('Point'),
            'coordinates': _Point1(_default)
        }
        super().__init__(rules, _parent=_parent, **kwargs)

GEOPoint = GEOPointField


class GEOLineField(GEOField):
    def __init__(self, _default=None, _parent=None, **kwargs):
        rules = {
            'type': _ConstString('LineString'),
            'coordinates': _Point2(_default)
        }
        super().__init__(rules, _parent=_parent, **kwargs)

GEOLine = GEOLineField


class GEOPolygonField(GEOField):
    def __init__(self, _default=None, _parent=None, **kwargs):
        rules = {
            'type': _ConstString('Polygon'),
            'coordinates': _Point4(_default)
        }
        super().__init__(rules, _parent=_parent, **kwargs)

GEOPolygon = GEOPolygonField


class GEOMultiPointField(GEOField):
    def __init__(self, _default=None, _parent=None, **kwargs):
        rules = {
            'type': _ConstString('MultiPoint'),
            'coordinates': _Point2(_default)
        }
        super().__init__(rules, _parent=_parent, **kwargs)

GEOMultiPoint = GEOMultiPointField


class GEOMultiLineField(GEOField):
    def __init__(self, _default=None, _parent=None, **kwargs):
        rules = {
            'type': _ConstString('MultiLineString'),
            'coordinates': _Point3(_default)
        }
        super().__init__(rules, _parent=_parent, **kwargs)

GEOMultiLine = GEOMultiLineField


class GEOMultiPolygonField(GEOField):
    def __init__(self, _default=None, _parent=None, **kwargs):
        rules = {
            'type': _ConstString('MultiPolygon'),
            'coordinates': _Point5(_default)
        }
        super().__init__(rules, _parent=_parent, **kwargs)

GEOMultiPolygon = GEOMultiPolygonField
