# coding: utf-8

import contextlib

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
        self._cache = []
        self._db_name = db_name

    @property
    def db_name(self):
        return self._db_name

    @contextlib.contextmanager
    def get_connection(self):
        if self._cache:
            conn = self._cache.pop(0)
        else:
            conn = Connection(self._uri)
            conn.simple_connect()
        try:
            yield conn
            if len(self._cache) < self._cache_size:
                self._cache.append(conn)
        except Exception:
            conn.close()
            raise

    def close(self):
        for i in self._cache:
            i.close()
        self._cache = []
