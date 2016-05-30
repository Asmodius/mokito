# coding: utf-8

from tornado.locks import Lock
from tornado.gen import coroutine, Return
from tornado.ioloop import IOLoop

from errors import TooManyConnections
from connection import Connection


class ConnectionPool(object):
    """Connection Pool to a single mongo instance.

    :Parameters:
      - `dbname`: mongo database name
      - `maxcached` (optional): maximum inactive cached connections for this pool. 0 for unlimited
      - `maxconnections` (optional): maximum open connections for this pool. 0 for unlimited
      - `slave_okay` (optional): is it okay to connect directly to and perform queries on a slave instance
      - `**kwargs`: passed to `connection.Connection`
    """

    def __init__(self,
                 uri,
                 dbname=None,
                 maxcached=0,
                 maxconnections=0,
                 slave_okay=False,
                 **kwargs):
        assert isinstance(dbname, (str, unicode, None.__class__))
        assert isinstance(maxcached, int)
        assert isinstance(maxconnections, int)
        assert isinstance(slave_okay, bool)
        if maxconnections:
            assert maxconnections >= maxcached

        self._kwargs = kwargs
        self._kwargs['pool'] = self
        self._kwargs['uri'] = uri
        self._maxcached = maxcached
        self._maxconnections = maxconnections
        self._idle_cache = []  # the actual connections that can be used
        self._idle_lock = Lock()
        self._dbname = dbname
        self._slave_okay = slave_okay

    @coroutine
    def get_connection(self):
        """ get a cached connection from the pool """
        with (yield self._idle_lock.acquire()):
            if self._idle_cache:
                raise Return(self._idle_cache.pop(0))

            if (self._maxconnections and self._maxconnections == len(self._idle_cache)):
                raise TooManyConnections("Too many connections: %d" % self._maxconnections)

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

            if not self._maxcached or len(self._idle_cache) < self._maxcached:
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
