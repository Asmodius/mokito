# coding: utf-8

from tornado.locks import Lock
from tornado.gen import coroutine, Return
from tornado.ioloop import IOLoop

from connection import Connection


class ConnectionPool(object):
    def __init__(self, uri, db_name, cache_size):
        """Connection Pool to a single mongo instance.

        :param uri: connection uri string
        :param db_name: mongo database name
        :param cache_size: (optional): maximum inactive cached connections for this pool
        """
        assert isinstance(db_name, (str, unicode))
        assert isinstance(cache_size, int)

        self._uri = uri
        self._cache_size = cache_size
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

        conn = Connection(self._uri, self)
        # IOLoop.current().spawn_callback(conn._run_conn_task)
        IOLoop.current().add_callback(conn._run_conn_task)
        yield conn._simple_connect()
        raise Return(conn)

    @coroutine
    def leave_connection(self, con, kill=False):
        with (yield self._idle_lock.acquire()):
            if con in self._idle_cache:
                raise Return()

        if not kill and self._cache_size < len(self._idle_cache):
            self._idle_cache.append(con)
        else:
            con.close()
