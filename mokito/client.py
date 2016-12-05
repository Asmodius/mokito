# coding: utf-8

from tornado.gen import coroutine, Return

from bson.son import SON

from pool import ConnectionPool
from errors import MokitoParamError
from cursor import Cursor


class Client(object):

    def __init__(self, db_name, uri='mongodb://127.0.0.1:27017', cache_size=10):
        """
        Client connection to represent a remote database.

        Internally Client maintains a pool of connections that will live beyond the life of this
        object.

        :param db_name: mongo database name
        :param uri: connection uri string
        :param cache_size: maximum inactive cached connections for this pool
        :return a Client instance that wraps a pool.ConnectionPool

        Usage:
            >>> import mokito
            >>> db = mokito.Client('db_name')
            >>> yield db.collection_name.find({...})
        """
        self._pool = ConnectionPool(uri, db_name, cache_size)
        self._db_name = db_name

    def __getattr__(self, name):
        """Get a collection by name."""
        return self.get_cursor(name)

    def __getitem__(self, name):
        """Get a collection by name."""
        return self.get_cursor(name)

    def get_cursor(self, collection_name):
        """Get a cursor to a collection by name.
        :param collection_name: the name of the collection
        :raise MokitoParamError on names with unallowable characters.
        """
        if not collection_name:
            raise MokitoParamError("collection names cannot be empty")
        if "$" in collection_name and \
                not (collection_name.startswith("oplog.$main") or
                     collection_name.startswith("$cmd")):
            raise MokitoParamError("collection names must not contain '$': %r" % collection_name)
        if collection_name.startswith(".") or collection_name.endswith("."):
            raise MokitoParamError('collection names must not start or end with ".": %r' %
                                   collection_name)
        if "\x00" in collection_name:
            raise MokitoParamError("collection names must not contain the null character")
        return Cursor(collection_name, self._pool)

    @coroutine
    def collection_names(self):
        res = yield self["system.namespaces"].find()
        names = [i['name'] for i in res if i['name'].count('.') == 1]
        strip = len(self._db_name) + 1
        raise Return([i[strip:] for i in names])

    @coroutine
    def command(self, command, value=1, **kwargs):
        """Issue a MongoDB command.

        Send command `command` to the database and return the response. If `command` is an instance
        of :class:`basestring` then the command {`command`: `value`} will be sent. Otherwise,
        `command` must be an instance of :class:`dict` and will be sent as is.

        Any additional keyword arguments will be added to the final command document before it is
        sent.

        :param command: document representing the command to be issued, or the name of the command
            (for simple commands only).
            .. note:: the order of keys in the `command` document is significant (the "verb" must
               come first), so commands which require multiple keys (e.g. `findandmodify`) should
               use an instance of :class:`~bson.son.SON` or a string and kwargs instead of a Python
               `dict`.
        :param value: (optional): value to use for the command verb when `command` is passed as a
            string
        :param kwargs: (optional): additional keyword arguments will be added to the command
          document before it is sent

        For example, a command like ``{buildinfo: 1}`` can be sent using:
        >>> import mokito
        >>> db = mokito.Client('db_name')
        >>> db.command("buildinfo")

        For a command where the value matters, like ``{collstats: collection_name}`` we can do:
        >>> db.command("collstats", 'collection_name')

        For commands that take additional arguments we can use kwargs. So
        ``{filemd5: object_id, root: file_root}`` becomes:
        >>> db.command("filemd5", object_id, root=file_root)
        """

        if isinstance(command, basestring):
            command = SON([(command, value)])
        command.update(kwargs)
        res = yield self.get_cursor("$cmd").command(command)
        raise Return(res)

    def close(self):
        self._pool.close()
