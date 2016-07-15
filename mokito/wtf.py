# coding: utf-8

import contextlib


class A(object):
    @contextlib.contextmanager
    def context(self):
        print u'вход в блок'
        try:
            yield 'XJ'
        except RuntimeError, err:
            print 'error: ', err
        finally:
            print u'выход из блока'


print 'B0'
a = A()
with a.context() as fp:
    print 'B1'
    print 'B2', fp

print 'B3'
