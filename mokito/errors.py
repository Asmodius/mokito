# coding: utf-8


class MokitoError(Exception):
    """Base class for all exceptions. """


class InvalidOperation(MokitoError):
    """Raised when a client attempts to perform an invalid operation."""


class InterfaceError(MokitoError):
    pass


class RSConnectionError(InterfaceError):
    pass


class DatabaseError(MokitoError):
    pass


class DataError(DatabaseError):
    pass


class IntegrityError(DatabaseError):

    def __init__(self, msg, code=None):
        self.code = code
        self.msg = msg

    def __unicode__(self):
        return u'IntegrityError: %s code:%s' % (self.msg, self.code or '')

    def __str__(self):
        return str(self.__unicode__())


class TooManyConnections(MokitoError):
    pass


class AuthenticationError(MokitoError):
    pass
