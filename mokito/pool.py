# coding: utf-8

from tornado.locks import Lock
from tornado.gen import coroutine, Return
from tornado.ioloop import IOLoop

from errors import TooManyConnections
from connection import Connection


class ConnectionPool(object):
    def __init__(self, uri, db_name, max_cached, max_connections, **kwargs):
        """Connection Pool to a single mongo instance.

        :param uri: connection uri string
        :param db_name: mongo database name
        :param max_cached: (optional): maximum inactive cached connections for this pool. 0 for
            unlimited
        :param max_connections: (optional): maximum open connections for this pool. 0 for unlimited
        :param kwargs: passed to `connection.Connection`
        """
        assert isinstance(db_name, (str, unicode))
        assert isinstance(max_cached, int)
        assert isinstance(max_connections, int)
        if max_connections:
            assert max_connections >= max_cached

        self._kwargs = kwargs
        self._kwargs['pool'] = self
        self._kwargs['uri'] = uri
        self._max_cached = max_cached
        self._max_connections = max_connections
        self._idle_cache = []  # the actual connections that can be used
        self._idle_lock = Lock()
        self._db_name = db_name

    @property
    def db_name(self):
        return self._db_name

    @coroutine
    def get_connection(self):
        """ get a cached connection from the pool """
        with (yield self._idle_lock.acquire()):
            if self._idle_cache:
                raise Return(self._idle_cache.pop(0))

            if self._max_connections and self._max_connections == len(self._idle_cache):
                raise TooManyConnections("Too many connections: %d" % self._max_connections)

        conn = Connection(**self._kwargs)
        # IOLoop.current().spawn_callback(conn._run_conn_task)
        IOLoop.current().add_callback(conn._run_conn_task)
        if 'dbuser' in self._kwargs and 'dbpass' in self._kwargs:
            yield conn._authorized_connect()
        elif 'rs' in self._kwargs:
            yield conn._rs_connect()
        else:
            yield conn._simple_connect()

        raise Return(conn)

    @coroutine
    def cache(self, con):
        """Put a dedicated connection back into the idle cache."""
        with (yield self._idle_lock.acquire()):
            if con in self._idle_cache:
                raise Return()

            if not self._max_cached or len(self._idle_cache) < self._max_cached:
                self._idle_cache.append(con)
            else:
                con._close()

#     def close(self):
#         """Close all connections in the pool."""
#         with (yield self._idle_lock.acquire()):
#             while self._idle_cache:  # close all idle connections
#                 con = self._idle_cache.pop(0)
#                 try:
#                     con._close()
#                 except:
#                     pass
