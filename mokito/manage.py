class ModelManager(object):
    models = {}

    @classmethod
    def add(cls, _class):
        cls.models[_class.__name__] = _class
