# coding: utf-8

from bson import SON, ObjectId

from tornado.gen import coroutine, Return

import message
from errors import DataError


class Cursor(object):
    """ 
    Cursor is a class used to call oeprations on a given db/collection using a 
    specific connection pool. it will transparently release connections back to 
    the pool after they receive responses
    """

    def __init__(self, collection, pool):
        assert isinstance(collection, (str, unicode))
        assert isinstance(pool, object)

        self.__collection = collection
        self.__pool = pool

    @property
    def dbname(self):
        return self.__pool._dbname

    def full_collection_name(self, collection=None):
        return u'%s.%s' % (self.dbname, collection or self.__collection)

    @coroutine
    def find_one(self, spec_or_id=None, fields=None):
        """Get a single document from the database.

        All arguments to `find` are also valid arguments for `find_one`,
        although any `limit` argument will be ignored. Returns a single 
        document, or ``None`` if no matching document is found.
        """
        if not (spec_or_id is None or isinstance(spec_or_id, dict)):
            try:
                spec_or_id = {"_id": ObjectId(spec_or_id)}
            except Exception as e:
                raise DataError(e.message)

        res = yield self.find(spec_or_id, fields, limit=-1)
        raise Return(res[0] if res else None)

    @coroutine
    def find(self, spec=None, fields=None, skip=0, limit=0, timeout=True,
             snapshot=False, tailable=False, sort=None, max_scan=None,
             slave_okay=False, _is_command=False, hint=None, comment=None):
        """Query the database.

        The `spec` argument is a prototype document that all results must match.
        For example:

        >>> db.test.find({"hello": "world"})

        only matches documents that have a key "hello" with value "world".  
        Matches can have other keys *in addition* to "hello". The `fields` 
        argument is used to specify a subset of fields that should be included 
        in the result documents. By limiting results to a certain subset of 
        fields you can cut down on network traffic and decoding time.

        :Parameters:
          - `spec` (optional): a SON object specifying elements which must be 
            present for a document to be included in the result set
          - `fields` (optional): a list of field names that should be returned 
            in the result set ("_id" will always be included), or a dict 
            specifying the fields to return
          - `skip` (optional): the number of documents to omit (from the start 
            of the result set) when returning the results
          - `limit` (optional): the maximum number of results to return
          - `timeout` (optional): if True, any returned cursor will be subject 
            to the normal timeout behavior of the mongod process. Otherwise, 
            the returned cursor will never timeout at the server. Care should 
            be taken to ensure that cursors with timeout turned off are 
            properly closed.
          - `snapshot` (optional): if True, snapshot mode will be used for this 
            query. Snapshot mode assures no duplicates are returned, or objects 
            missed, which were present at both the start and end of the query's 
            execution. For details, see the `snapshot documentation
            <http://dochub.mongodb.org/core/snapshot>`_.
          - `tailable` (optional): the result of this find call will be a 
            tailable cursor - tailable cursors aren't closed when the last data 
            is retrieved but are kept open and the cursors location marks the 
            final document's position. if more data is received iteration of 
            the cursor will continue from the last document received. For 
            details, see the `tailable cursor documentation
            <http://www.mongodb.org/display/DOCS/Tailable+Cursors>`_.
          - `sort` (optional): a list of (key, direction) pairs specifying the 
            sort order for this query. See `~pymongo.cursor.Cursor.sort` for 
            details.
          - `max_scan` (optional): limit the number of documents examined when 
            performing the query
          - `slave_okay` (optional): is it okay to connect directly to and 
            perform queries on a slave instance
        """

        def query_options():
            options = 0
            if tailable:
                options |= message._QUERY_OPTIONS["tailable_cursor"]
            if slave_okay or self.__pool._slave_okay:
                options |= message._QUERY_OPTIONS["slave_okay"]
            if not timeout:
                options |= message._QUERY_OPTIONS["no_timeout"]
            return options

        if spec is None:
            spec = {}

        if not _is_command and "$query" not in spec:
            spec = SON({"$query": spec})
        ordering = sort and message._index_document(sort) or None
        if ordering:
            spec["$orderby"] = ordering
        if hint:
            spec["$hint"] = hint
        if comment:
            spec["$comment"] = comment
        if snapshot:
            spec["$snapshot"] = True
        if max_scan:
            spec["$maxScan"] = max_scan

        if limit is None:
            limit = 0

        if skip is None:
            skip = 0

        if fields and not isinstance(fields, dict):
            fields = dict((i, 1) for i in fields)

        connection = yield self.__pool.get_connection()
        try:
            request_id, data = message.query(query_options(), self.full_collection_name(), skip, limit, spec, fields)
            res = yield connection.send_message(request_id, data)
            request_id, data = message.kill_cursors([res['cursor_id']])
            yield connection.send_message(request_id, data, False)
        except:
            connection.close()
            raise

        raise Return(res['data'])

    @coroutine
    def insert(self, doc_or_docs, safe=True, check_keys=True, **kwargs):
        """Insert a document(s) into this collection.

        If `safe` is ``True`` then the insert will be checked for errors, 
        raising :class:`~pymongo.errors.OperationFailure` if one occurred. Safe 
        inserts wait for a response from the database, while normal inserts do 
        not.

        Any additional keyword arguments imply ``safe=True``, and will be used 
        as options for the resultant `getLastError` command. For example, to 
        wait for replication to 3 nodes, pass ``w=3``.

        :Parameters:
          - `doc_or_docs`: a document or list of documents to be inserted
          - `safe` (optional): check that the insert succeeded?
          - `check_keys` (optional): check if keys start with '$' or
            contain '.', raising :class:`~pymongo.errors.InvalidName`
            in either case
          - `**kwargs` (optional): any additional arguments imply ``safe=True``, 
            and will be used as options for the `getLastError` command
        """
        if not isinstance(safe, bool):
            raise TypeError("safe must be an instance of bool")

        docs = doc_or_docs
        if isinstance(docs, dict):
            docs = [docs]

        for i in docs:
            if not '_id' in i:
                i['_id'] = ObjectId()
        _ids = [i['_id'] for i in docs]

        if kwargs:
            safe = True

        connection = yield self.__pool.get_connection()
        try:
            request_id, data = message.insert(self.full_collection_name(), docs, check_keys, safe, kwargs)
            yield connection.send_message(request_id, data, safe)
        except:
            connection.close()
            raise

        if len(docs) == 1:
            _ids = _ids[0]
        raise Return(_ids)

    @coroutine
    def update(self, spec, document, upsert=False, safe=True, multi=False, **kwargs):
        """Update a document(s) in this collection.

        Raises :class:`TypeError` if either `spec` or `document` is
        not an instance of ``dict`` or `upsert` is not an instance of
        ``bool``. If `safe` is ``True`` then the update will be
        checked for errors, raising
        :class:`~pymongo.errors.OperationFailure` if one
        occurred. Safe updates require a response from the database,
        while normal updates do not - thus, setting `safe` to ``True``
        will negatively impact performance.

        There are many useful `update modifiers`_ which can be used
        when performing updates. For example, here we use the
        ``"$set"`` modifier to modify some fields in a matching
        document:

          >>> db.test.insert({"x": "y", "a": "b"})
          ObjectId('...')
          >>> list(db.test.find())
          [{u'a': u'b', u'x': u'y', u'_id': ObjectId('...')}]
          >>> db.test.update({"x": "y"}, {"$set": {"a": "c"}})
          >>> list(db.test.find())
          [{u'a': u'c', u'x': u'y', u'_id': ObjectId('...')}]

        If `safe` is ``True`` returns the response to the *lastError*
        command. Otherwise, returns ``None``.

        # Any additional keyword arguments imply ``safe=True``, and will
        # be used as options for the resultant `getLastError`
        # command. For example, to wait for replication to 3 nodes, pass
        # ``w=3``.

        :Parameters:
          - `spec`: a ``dict`` or :class:`~bson.son.SON` instance
            specifying elements which must be present for a document
            to be updated
          - `document`: a ``dict`` or :class:`~bson.son.SON`
            instance specifying the document to be used for the update
            or (in the case of an upsert) insert - see docs on MongoDB
            `update modifiers`_
          - `upsert` (optional): perform an upsert if ``True``
          - `safe` (optional): check that the update succeeded?
          - `multi` (optional): update all documents that match
            `spec`, rather than just the first matching document. The
            default value for `multi` is currently ``False``, but this
            might eventually change to ``True``. It is recommended
            that you specify this argument explicitly for all update
            operations in order to prepare your code for that change.
          - `**kwargs` (optional): any additional arguments imply
            ``safe=True``, and will be used as options for the
            `getLastError` command

        .. _update modifiers: http://www.mongodb.org/display/DOCS/Updating
        """
        if not isinstance(spec, dict):
            raise TypeError("spec must be an instance of dict")
        if not isinstance(document, dict):
            raise TypeError("document must be an instance of dict")
        if not isinstance(upsert, bool):
            raise TypeError("upsert must be an instance of bool")
        if not isinstance(safe, bool):
            raise TypeError("safe must be an instance of bool")

        if kwargs:
            safe = True

        connection = yield self.__pool.get_connection()
        try:
            request_id, data = message.update(self.full_collection_name(), upsert, multi, spec, document, safe, kwargs)
            res = yield connection.send_message(request_id, data, safe)
        except:
            connection.close()
            raise

        if safe:
            raise Return(res['data'][0].get('upserted', None))

    @coroutine
    def remove(self, spec_or_id=None, safe=True, **kwargs):
        if not isinstance(safe, bool):
            raise TypeError("safe must be an instance of bool")

        if spec_or_id is None:
            spec_or_id = {}
        if not isinstance(spec_or_id, dict):
            spec_or_id = {"_id": spec_or_id}

        if kwargs:
            safe = True

        connection = yield self.__pool.get_connection()
        try:
            request_id, data = message.delete(self.full_collection_name(), spec_or_id, safe, kwargs)
            res = yield connection.send_message(request_id, data, safe)
        except:
            connection.close()
            raise

        if safe:
            raise Return(res['data'][0].get('n', 0))

    @coroutine
    def count(self, spec=None):
        def query_options():
            options = 0
            return options

        if spec is None:
            spec = {}
        spec = SON({'count': self.__collection, "query": spec})

        connection = yield self.__pool.get_connection()
        try:
            request_id, data = message.query(query_options(), self.full_collection_name('$cmd'), 0, -1, spec)
            res = yield connection.send_message(request_id, data)
        except:
            connection.close()
            raise

        raise Return(res['data'][0]['n'])
