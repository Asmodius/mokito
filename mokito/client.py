# coding: utf-8

from tornado.gen import coroutine, Return

from bson.son import SON

from pool import ConnectionPool
from errors import DataError
from cursor import Cursor
from orm import _all_clients


class Client(object):

    def __init__(self, uri, **kwargs):
        """
        Client connection to represent a remote database.

        Internally Client maintains a pool of connections that will live beyond the life of this object.

        :Parameters:
          - `**kwargs`: passed to `pool.ConnectionPool`
              - `dbname`: mongo database name
              - `maxcached` (optional): maximum inactive cached connections for this pool. 0 for unlimited
              - `maxconnections` (optional): maximum open connections for this pool. 0 for unlimited
          - `**kwargs`: passed to `connection.Connection`
              - `uri`: port to connect to 
              - `slave_okay` (optional): is it okay to connect directly to and perform queries on a slave instance
              - `autoreconnect` (optional): auto reconnect on interface errors

        @returns a `Client` instance that wraps a `pool.ConnectionPool`

        Usage:
            >>> db = mokito.Client(host=host, port=port, dbname=dbname)
            >>> yield db.collectionname.find({...})
        """
        self._pool = ConnectionPool(uri, **kwargs)
        _all_clients[self._pool._dbname] = self

    def __getattr__(self, name):
        """Get a collection by name."""
        return self.get_cursor(name)

    def __getitem__(self, name):
        """Get a collection by name."""
        return self.get_cursor(name)

    def get_cursor(self, collectionname):
        """Get a cursor to a collection by name.
        raises `DataError` on names with unallowable characters.
        :Parameters:
          - `collectionname`: the name of the collection
          - `dbname`: (optional) overide the default db for a connection
        """
        if not collectionname:
            raise DataError("collection names cannot be empty")
        if "$" in collectionname and not (collectionname.startswith("oplog.$main") or
                                          collectionname.startswith("$cmd")):
            raise DataError("collection names must not contain '$': %r" % collectionname)
        if collectionname.startswith(".") or collectionname.endswith("."):
            raise DataError("collecion names must not start or end with '.': %r" % collectionname)
        if "\x00" in collectionname:
            raise DataError("collection names must not contain the null character")
        return Cursor(collectionname, self._pool)

    @coroutine
    def collection_names(self):
        res = yield self["system.namespaces"].find(_must_use_master=True)
        names = [i['name'] for i in res if i['name'].count('.') == 1]
        strip = len(self._pool._dbname) + 1
        raise Return([i[strip:] for i in names])

    @coroutine
    def command(self, command, value=1, check=True, allowable_errors=[], **kwargs):
        """Issue a MongoDB command.

        Send command `command` to the database and return the
        response. If `command` is an instance of :class:`basestring`
        then the command {`command`: `value`} will be sent. Otherwise,
        `command` must be an instance of :class:`dict` and will be
        sent as is.

        Any additional keyword arguments will be added to the final
        command document before it is sent.

        For example, a command like ``{buildinfo: 1}`` can be sent using:

        >>> db.command("buildinfo")

        For a command where the value matters, like ``{collstats:
        collection_name}`` we can do:

        >>> db.command("collstats", collection_name)

        For commands that take additional arguments we can use
        kwargs. So ``{filemd5: object_id, root: file_root}`` becomes:

        >>> db.command("filemd5", object_id, root=file_root)

        :Parameters:
          - `command`: document representing the command to be issued,
            or the name of the command (for simple commands only).

            .. note:: the order of keys in the `command` document is
               significant (the "verb" must come first), so commands
               which require multiple keys (e.g. `findandmodify`)
               should use an instance of :class:`~bson.son.SON` or
               a string and kwargs instead of a Python `dict`.

          - `value` (optional): value to use for the command verb when
             `command` is passed as a string
          - `**kwargs` (optional): additional keyword arguments will
            be added to the command document before it is sent
        """

        if isinstance(command, basestring):
            command = SON([(command, value)])
        command.update(kwargs)
        res = yield self.get_cursor("$cmd").find_one(command, _must_use_master=True, _is_command=True)
        raise Return(res)
