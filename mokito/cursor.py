# coding: utf-8

from bson import SON, ObjectId

from tornado.gen import coroutine, Return

import message
from errors import MokitoParamError
from tools import fields2sort


class Cursor(object):
    """Cursor is a class used to call oeprations on a given db/collection using a specific
    connection pool. it will transparently release connections back to the pool after they receive
    responses
    """

    def __init__(self, collection_name, pool):
        assert isinstance(collection_name, basestring)
        assert isinstance(pool, object)

        self.__collection_name = collection_name
        self.__pool = pool

    @property
    def db_name(self):
        return self.__pool.db_name

    @property
    def collection_name(self):
        return self.__collection_name

    def _full_collection_name(self, collection=None):
        return u'%s.%s' % (self.db_name, collection or self.__collection_name)

    @property
    def full_collection_name(self):
        return self._full_collection_name()

    @coroutine
    def find_one(self, spec_or_id=None, fields=None, skip=0, sort=None, _is_command=False):
        """Get a single document from the database.

        All arguments to `find` are also valid arguments for `find_one`, although any `limit`
        argument will be ignored. Returns a single document, or ``None`` if no matching document is
        found.
        """
        if not (spec_or_id is None or isinstance(spec_or_id, dict)):
            try:
                spec_or_id = {"_id": ObjectId(spec_or_id)}
            except Exception as e:
                raise MokitoParamError(e.message)

        res = yield self.find(spec_or_id, fields, skip, limit=1,
                              sort=sort, _is_command=_is_command)
        raise Return(res[0] if res else None)

    @coroutine
    def find(self, spec=None, fields=None, skip=0, limit=0, snapshot=False, tailable=False,
             sort=None, max_scan=None, _is_command=False, hint=None):
        """Query the database.
        :param spec: (optional): _id or dict
        :param fields: (optional): a list of field names that should be returned in the result set
            ("_id" will always be included), or a dict specifying the fields to return
        :param skip: (optional): the number of documents to omit (from the start of the result set)
            when returning the results
        :param limit: (optional): the maximum number of results to return
        :param snapshot: (optional): if True, snapshot mode will be used for this query. Snapshot
            mode assures no duplicates are returned, or objects missed, which were present at both
            the start and end of the query's execution. For details, see the snapshot documentation
            <http://dochub.mongodb.org/core/snapshot>
        :param tailable: (optional): the result of this find call will be a tailable cursor -
            tailable cursors aren't closed when the last data is retrieved but are kept open and
            the cursors location marks the final document's position. if more data is received
            iteration of the cursor will continue from the last document received. For details, see
            the tailable cursor documentation
            <https://docs.mongodb.com/manual/core/tailable-cursors/>
            <https://docs.mongodb.com/manual/reference/method/cursor.tailable/>
        :param sort: (optional):
            1) a list of (key, direction) pairs specifying the sort order for this query. See
               `pymongo.cursor.Cursor.sort` for details.
            2) a field name or list of field names with the sign of sorting direction ['f1', '-f2']
        :param max_scan: (optional): limit the number of documents examined when performing the
            query
        :param _is_command:
        :param hint: override MongoDB’s default index selection
            <https://docs.mongodb.com/manual/reference/method/cursor.hint/>
        """
        def query_options():
            options = 0
            if tailable:
                options |= message._QUERY_OPTIONS["tailable_cursor"]
            return options

        if spec is None:
            spec = {}
        elif isinstance(spec, ObjectId):
            spec = {"_id": spec}
        if not _is_command and "$query" not in spec:
            spec = SON({"$query": spec})

        if sort:
            sort = message.index_document(fields2sort(sort))
            if sort:
                spec["$orderby"] = sort

        if hint:
            spec["$hint"] = hint
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

        request_id, data = message.query(query_options(), self.full_collection_name,
                                         skip, limit, spec, fields)
        with self.__pool.get_connection() as conn:
            res = yield conn.send_message(request_id, data)
            request_id, data = message.kill_cursors([res['cursor_id']])
            yield conn.send_message(request_id, data, False)

        raise Return(res['data'])

    @coroutine
    def insert(self, doc_or_docs, safe=True, check_keys=True, **kwargs):
        """Insert a document(s) into this collection.

        :param doc_or_docs: a document or list of documents to be inserted
        :param safe: (optional): check that the insert succeeded
        :param check_keys: (optional): check if keys start with '$' or contain '.',
            raising `pymongo.errors.InvalidName` in either case. If `safe` is `True` then the
            insert will be checked for errors, raising `pymongo.errors.OperationFailure` if one
            occurred. Safe inserts wait for a response from the database, while normal inserts do
            not.
        :param kwargs: (optional): any additional arguments imply `safe=True`, and will be used as
            options for the `getLastError` command
        """
        docs = doc_or_docs
        if isinstance(docs, dict):
            docs = [docs]

        for i in docs:
            if '_id' not in i:
                i['_id'] = ObjectId()
        _ids = [i['_id'] for i in docs]

        safe = True if kwargs else bool(safe)

        request_id, data = message.insert(self.full_collection_name, docs,
                                          check_keys, safe, kwargs)
        with self.__pool.get_connection() as conn:
            yield conn.send_message(request_id, data, safe)

        if len(docs) == 1:
            _ids = _ids[0]
        raise Return(_ids)

    @coroutine
    def update(self, spec, document, upsert=False, safe=True, multi=False,
               no_replace=False, **kwargs):
        """Update a document(s) in this collection.

        :param spec: a dict or bson.son.SON instance specifying elements which must be present for
            a document to be updated
        :param document: a dict or bson.son.SON instance specifying the document to be used for the
            update or (in the case of an upsert) insert
        :param upsert: perform an upsert if True
        :param safe: (optional): check that the update succeeded
        :param multi: (optional): update all documents that match `spec`, rather than just the
            first matching document. The default value for `multi` is currently `False`, but this
            might eventually change to `True`. It is recommended that you specify this argument
            explicitly for all update operations in order to prepare your code for that change.
        :param no_replace: if `True` then {document} => {$set: {document}}
        :param kwargs: (optional): any additional arguments imply `safe=True`, and will be used as
            options for the `getLastError` command
        :raise TypeError: if either `spec` or `document` is not an instance of `dict`.
        :raise OperationFailure: If `safe` is `True` then the update will be checked for errors,
            raising `pymongo.errors.OperationFailure` if one occurred. Safe updates require a
            response from the database, while normal updates do not - thus, setting `safe` to
            `True` will negatively impact performance.

        There are many useful `update modifiers`_ which can be used when performing updates. For
        example, here we use the "$set" modifier to modify some fields in a matching document:

          >>> db.test.insert({"x": "y", "a": "b"})
          ObjectId('...')
          >>> list(db.test.find())
          [{u'a': u'b', u'x': u'y', u'_id': ObjectId('...')}]
          >>> db.test.update({"x": "y"}, {"$set": {"a": "c"}})
          >>> list(db.test.find())
          [{u'a': u'c', u'x': u'y', u'_id': ObjectId('...')}]
        """
        if not isinstance(spec, dict):
            raise TypeError("spec must be an instance of dict")
        if not isinstance(document, dict):
            raise TypeError("document must be an instance of dict")

        upsert = bool(upsert)
        safe = True if kwargs else bool(safe)
        if no_replace and not document.get("$set"):
            document = {"$set": document}

        request_id, data = message.update(self.full_collection_name, upsert, multi, spec,
                                          document, safe, kwargs)
        with self.__pool.get_connection() as conn:
            res = yield conn.send_message(request_id, data, safe)

        if safe:
            raise Return(res['data'][0].get('upserted', None))

    @coroutine
    def remove(self, spec_or_id=None, safe=True, **kwargs):
        if spec_or_id is None:
            spec_or_id = {}
        if not isinstance(spec_or_id, dict):
            spec_or_id = {"_id": spec_or_id}

        safe = True if kwargs else bool(safe)

        request_id, data = message.delete(self.full_collection_name, spec_or_id, safe, kwargs)
        with self.__pool.get_connection() as conn:
            res = yield conn.send_message(request_id, data, safe)

        if safe:
            raise Return(res['data'][0].get('n', 0))

    @coroutine
    def count(self, spec=None, hint=None):
        if spec is None:
            spec = {}
        spec = SON({'count': self.__collection_name, "query": spec})

        if hint:
            spec["$hint"] = hint

        request_id, data = message.query(0, self._full_collection_name('$cmd'), 0, -1, spec)
        with self.__pool.get_connection() as conn:
            res = yield conn.send_message(request_id, data)

        raise Return(res['data'][0]['n'])

    @coroutine
    def distinct(self, key, spec=None):
        if spec is None:
            spec = {}
        spec = SON({"distinct": self.__collection_name, "key": key, "query": spec})

        request_id, data = message.query(0, self._full_collection_name('$cmd'), 0, -1, spec)
        with self.__pool.get_connection() as conn:
            res = yield conn.send_message(request_id, data)

        raise Return(res['data'][0]['values'])
