"""Tools for creating `messages
<http://www.mongodb.org/display/DOCS/Mongo+Wire+Protocol>
"""

import random
import struct

from bson import BSON, _make_c_string, decode_all, DEFAULT_CODEC_OPTIONS, SON

from errors import (
    MokitoEmptyBulkError,
    MokitoDriverError,
    MokitoMasterChangedError,
    MokitoInvalidCursorError
)

MAX_INT32 = 2147483647
MIN_INT32 = -2147483648

ASCENDING = 1
"""Ascending sort order."""
DESCENDING = -1
"""Descending sort order."""

GEO2D = "2d"
"""Index specifier for a 2-dimensional `geospatial index`_.

.. _geospatial index: http://docs.mongodb.org/manual/core/2d/
"""


def _randint():
    """Generate a pseudo random 32 bit integer."""
    return random.randint(MIN_INT32, MAX_INT32)


_ZERO_32 = b'\x00\x00\x00\x00'


def __last_error(args):
    """Data to send to do a lastError."""
    cmd = SON([("getlasterror", 1)])
    cmd.update(args)
    return query(0, "admin.$cmd", 0, -1, cmd)

QUERY_OPTIONS = {
    "tailable_cursor": 2,
    "slave_okay": 4,
    "oplog_replay": 8,
    "no_timeout": 16
}

# OP_REPLY = 1  # Reply to a client request. responseTo is set.
# OP_MSG = 1000  # Generic msg command followed by a string.
OP_UPDATE = 2001  # Update document.
OP_INSERT = 2002  # Insert new document.
OP_QUERY = 2004  # Query a collection.
OP_GET_MORE = 2005  # Get more data from a query. See Cursors.
OP_DELETE = 2006  # Delete documents.
OP_KILL_CURSORS = 2007  # Notify database that the client has finished with the cursor.


def __pack_message(operation, data):
    """Takes message data and adds a message header based on the operation.

    Returns the resultant message string.
    """
    request_id = _randint()
    message = struct.pack("<i", 16 + len(data))
    message += struct.pack("<i", request_id)
    message += _ZERO_32
    message += struct.pack("<i", operation)
    return request_id, message + data


def query(options, collection_name, num_to_skip, num_to_return, request, field_selector=None):
    """Get a **query** message. """
    data = struct.pack("<I", options)
    data += _make_c_string(collection_name)
    data += struct.pack("<i", num_to_skip)
    data += struct.pack("<i", num_to_return)
    data += BSON.encode(request)
    if field_selector:
        data += BSON.encode(field_selector)
    return __pack_message(OP_QUERY, data)


def get_more(collection_name, num_to_return, cursor_id):
    """Get a **getMore** message."""
    data = _ZERO_32
    data += _make_c_string(collection_name)
    data += struct.pack("<i", num_to_return)
    data += struct.pack("<q", cursor_id)
    return __pack_message(OP_GET_MORE, data)


def insert(collection_name, docs, check_keys, safe, last_error_args):
    """Get an **insert** message. """
    data = _ZERO_32
    data += _make_c_string(collection_name)
    bson_data = "".join([BSON.encode(doc, check_keys) for doc in docs])
    if not bson_data:
        raise MokitoEmptyBulkError()
    data += bson_data
    if safe:
        (_, insert_message) = __pack_message(OP_INSERT, data)
        (request_id, error_message) = __last_error(last_error_args)
        return request_id, insert_message + error_message
    else:
        return __pack_message(OP_INSERT, data)


def update(collection_name, upsert, multi, spec, doc, safe, last_error_args):
    """Get an **update** message."""
    options = 0
    if upsert:
        options += 1
    if multi:
        options += 2

    data = _ZERO_32
    data += _make_c_string(collection_name)
    data += struct.pack("<i", options)
    data += BSON.encode(spec)
    data += BSON.encode(doc)
    if safe:
        (_, update_message) = __pack_message(OP_UPDATE, data)
        (request_id, error_message) = __last_error(last_error_args)
        return request_id, update_message + error_message
    else:
        return __pack_message(OP_UPDATE, data)


def delete(collection_name, spec, safe, last_error_args):
    """Get a **delete** message."""
    data = _ZERO_32
    data += _make_c_string(collection_name)
    data += _ZERO_32
    data += BSON.encode(spec)
    if safe:
        (_, remove_message) = __pack_message(OP_DELETE, data)
        (request_id, error_message) = __last_error(last_error_args)
        return request_id, remove_message + error_message
    else:
        return __pack_message(OP_DELETE, data)


def kill_cursors(*cursor_ids):
    """Get a **killCursors** message."""
    data = _ZERO_32
    data += struct.pack("<i", len(cursor_ids))
    for cursor_id in cursor_ids:
        data += struct.pack("<q", cursor_id)
    return __pack_message(OP_KILL_CURSORS, data)


def unpack_response(response):
    """Unpack a response from the database.

    Check the response for errors and unpack, returning a dictionary containing the response data.
    :Parameters:
      - `response`: byte string as returned from the database
      - `cursor_id`: cursor_id we sent to get this response - used for raising an informative
      exception when we get cursor id not valid at server response
    """
    response_flag = struct.unpack("<i", response[:4])[0]
    if response_flag & 1:
        # Shouldn't get this response if we aren't doing a getMore
        raise MokitoInvalidCursorError()

    elif response_flag & 2:
        error_object = BSON(response[20:]).decode()
        if error_object["$err"] == "not master":
            raise MokitoMasterChangedError()
        raise MokitoDriverError("MongoDB: %s" % error_object["$err"])

    result = {"cursor_id": struct.unpack("<q", response[4:12])[0],
              "starting_from": struct.unpack("<i", response[12:16])[0],
              "number_returned": struct.unpack("<i", response[16:20])[0],
              "data": decode_all(response[20:], DEFAULT_CODEC_OPTIONS)}

    assert len(result["data"]) == result["number_returned"]
    return result


def index_document(index_list):
    """Helper to generate an index specifying document.
    Takes a list of (key, direction) pairs.
    """
    if isinstance(index_list, dict):
        raise TypeError("passing a dict to sort/create_index/hint is not "
                        "allowed - use a list of tuples instead. did you "
                        "mean %r?" % list(index_list.iteritems()))
    elif not isinstance(index_list, list):
        raise TypeError("must use a list of (key, direction) pairs, not: " + repr(index_list))
    if not len(index_list):
        raise ValueError("key_or_list must not be the empty list")

    index = SON()
    for (key, value) in index_list:
        if not isinstance(key, basestring):
            raise TypeError("first item in each key pair must be a string")
        if value not in [ASCENDING, DESCENDING, GEO2D]:
            raise TypeError("second item in each key pair must be ASCENDING, DESCENDING, or GEO2D")
        index[key] = value
    return index

# def _password_digest(username, password):
#     """Get a password digest to use for authentication.
#     """
#     if not isinstance(password, basestring):
#         raise TypeError("password must be an instance of basestring")
#     if not isinstance(username, basestring):
#         raise TypeError("username must be an instance of basestring")
#
#     md5hash = hashlib.md5()
#     md5hash.update("%s:mongo:%s" % (username.encode('utf-8'),
#                                     password.encode('utf-8')))
#     return unicode(md5hash.hexdigest())
#
#
# def _auth_key(nonce, username, password):
#     """Get an auth key to use for authentication.
#     """
#     digest = _password_digest(username, password)
#     md5hash = hashlib.md5()
#     md5hash.update("%s%s%s" % (nonce, unicode(username), digest))
#     return unicode(md5hash.hexdigest())
