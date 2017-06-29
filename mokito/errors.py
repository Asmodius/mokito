class MokitoError(Exception):
    """Base class for all exceptions. """


# class MokitoDriverError(MokitoError):
#     pass
#
#
# class MokitoEmptyBulkError(MokitoDriverError):
#     message = "cannot do an empty bulk insert"
#
#
# class MokitoMasterChangedError(MokitoDriverError):
#     message = "master has changed"
#
#
# class MokitoInvalidURIError(MokitoDriverError):
#     message = "Invalid URI"
#
#
# class MokitoInvalidCursorError(MokitoDriverError):
#     message = "Cursor not valid at server"
#
#
# class MokitoParamError(MokitoDriverError):
#     message = "Invalid parameters"
#
#
# class MokitoConnectionError(MokitoDriverError):
#     pass
#
#
# class MokitoResponseError(MokitoDriverError):
#
#     def __init__(self, msg, code=None):
#         self.code = code
#         self.msg = msg
#
#     def __unicode__(self):
#         return u'Response error: %s code:%s' % (self.msg, self.code or '')
#
#     def __str__(self):
#         return str(self.__unicode__())


class MokitoORMError(MokitoError):
    pass


class MokitoDBREFError(MokitoORMError):
    pass


class MokitoChoiceError(MokitoORMError):
    pass
