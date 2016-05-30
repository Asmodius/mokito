# coding: utf-8

import socket
import struct
import urlparse
from functools import partial

from tornado.iostream import IOStream
from tornado.gen import coroutine, Return
from tornado.concurrent import Future
from tornado.ioloop import IOLoop

from errors import IntegrityError, InterfaceError
from message import _unpack_response


class Connection(object):

    def __init__(self, uri, pool, **kwargs):
        """
        :Parameters:
          - `autoreconnect` (optional): auto reconnect on interface errors
          - `seed`: seed list to connect to a replica set (required when replica sets are used)
          - `secondary_only`: (optional, only useful for replica set connections)
             if true, connect to a secondary member only
        """
        _uri = urlparse.urlparse(uri)
        self._host = _uri.hostname
        self._port = int(_uri.port or 27017)
        self._dbuser = _uri.username
        self._dbpass = _uri.password
        _q = urlparse.parse_qs(_uri.query or '')
        self._rs = _q.get('replicaSet', None)

        #self._seed = seed
        #self._secondary_only = secondary_only
        self.__stream = None
        self.__alive = False
        #self.__autoreconnect = autoreconnect
        self.__pool = pool

        self.e_conn = Future()

    def _run_conn_task(self):
        self.e_conn.set_result(None)
        self.__alive = True

    @coroutine
    def _simple_connect(self):
        yield self.e_conn
        try:
            self.__stream = IOStream(socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0))
            self.__stream.connect((self._host, self._port))
        except socket.error as e:
            raise InterfaceError(e)

    @coroutine
    def _authorized_connect(self):
        print 'M3'
        # yield self.e_run.wait()
        yield self.e_conn
        #self.__job_queue.append(asyncjobs.AuthorizeJob(self, self._dbuser, self._dbpass, self.__pool, err_callback))
        print 'M4'

    @coroutine
    def _rs_connect(self):
        print 'M5'
        # yield self.e_run.wait()
        yield self.e_conn
        #self.__job_queue.append(asyncjobs.ConnectRSJob(self, self._seed, self._rs, self._secondary_only, err_callback))
        print 'M6'

    def close(self):
        self.__pool.cache(self)

    def _close(self):
        """close the socket and cleanup"""
        if not self.__alive:
            raise InterfaceError('connection closed')
        #self.__job_queue = []
        self.__alive = False
        self.__stream.close()

    @coroutine
    def send_message(self, request_id, data, safe=True):
        #         if not self.__alive:
        #             if self.__autoreconnect:
        #                 self.__connect(err_callback)
        #             else:
        #                 raise InterfaceError('connection invalid. autoreconnect=False')

        xx = Future()
        IOLoop.current().add_callback(partial(lambda x: x.set_result(None), xx))
        res = yield self._send_message(request_id, data, safe, xx)
        raise Return(res)

    @coroutine
    def _send_message(self, request_id, data, safe, future):
        yield future

        try:
            self.__stream.write(data)
            if safe:
                length = yield self._get_header(request_id)
                res = yield self._get_response(length - 16)
                raise Return(res)
        except IOError:
            self.__alive = False
            raise

    @coroutine
    def _get_header(self, request_id):
        header = yield self.__stream.read_bytes(16)
        length = int(struct.unpack("<i", header[:4])[0])
        _request_id = struct.unpack("<i", header[8:12])[0]
        assert request_id == _request_id, "ids don't match %r %r" % (request_id, _request_id)
        assert 1 == struct.unpack("<i", header[12:])[0]
        raise Return(length)

    @coroutine
    def _get_response(self, length):
        response = yield self.__stream.read_bytes(length)
        response = _unpack_response(response)
        if response and response['data'] and response['data'][0].get('err') and response['data'][0].get('code'):
            raise IntegrityError(response['data'][0]['err'], code=response['data'][0]['code'])
        raise Return(response)
