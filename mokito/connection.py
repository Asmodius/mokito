# coding: utf-8

import socket
import struct
import urlparse
from functools import partial

from tornado.iostream import IOStream
from tornado.gen import coroutine, Return
from tornado.concurrent import Future
from tornado.ioloop import IOLoop

from errors import (
    MokitoResponseError,
    MokitoInvalidURIError,
    MokitoConnectionError
)
from message import unpack_response


class Connection(object):

    def __init__(self, uri):
        try:
            _uri = urlparse.urlparse(uri)
            self._host = _uri.hostname
            self._port = int(_uri.port or 27017)
        except:
            raise MokitoInvalidURIError()

        self.__stream = None

    def simple_connect(self):
        try:
            self.__stream = IOStream(socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0))
            self.__stream.connect((self._host, self._port))
        except socket.error as e:
            raise MokitoConnectionError(e)

    def close(self):
        self.__stream.close()

    @coroutine
    def send_message(self, request, safe=True):
        xx = Future()
        IOLoop.current().add_callback(partial(lambda x: x.set_result(None), xx))
        res = yield self._send_message(request, safe, xx)
        raise Return(res)

    @coroutine
    def _send_message(self, request, safe, future):
        yield future

        self.__stream.write(request[1])
        if safe:
            length = yield self._get_header(request[0])
            res = yield self._get_response(length - 16)
            raise Return(res)

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
        response = unpack_response(response)
        if response and response['data'] and response['data'][0].get('err') and \
                response['data'][0].get('code'):
            raise MokitoResponseError(response['data'][0]['err'], code=response['data'][0]['code'])
        raise Return(response)
