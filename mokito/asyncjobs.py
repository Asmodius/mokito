"""Tools for creating `messages
<http://www.mongodb.org/display/DOCS/Mongo+Wire+Protocol>`_ to be sent to MongoDB.

.. note:: This module is for internal use and is generally not needed by
   application developers.
"""

# import random
# from bson import SON
#
# import message
# import helpers
# from errors import AuthenticationError, RSConnectionError, InterfaceError
#
# def _parse_host(h):
#     try:
#         host, port = h.split(":", 1)
#         port = int(port)
#     except ValueError:
#         raise ValueError("Wrong host:port value: %s" % h)
#
#     return host, port
#
# class AsyncJob(object):
#
#     def __init__(self, connection, state, err_callback):
#         self.connection = connection
#         self._err_callback = err_callback
#         self._state = state
#
#     def _error(self, e):
#         self.connection.close()
#         if self._err_callback:
#             self._err_callback(e)
#
#     def update_err_callback(self, err_callback):
#         self._err_callback = err_callback
#
#     def __repr__(self):
#         return "%s at 0x%X, state = %r" % (self.__class__.__name__, id(self), self._state)
#
#
# class AuthorizeJob(AsyncJob):
#
#     def __init__(self, connection, dbuser, dbpass, pool, err_callback):
#         super(AuthorizeJob, self).__init__(connection, "start", err_callback)
#         self.dbuser = dbuser
#         self.dbpass = dbpass
#         self.pool = pool
#
#     def process(self, response=None, error=None):
#         if error:
#             self._error(AuthenticationError(error))
#             return
#
#         if self._state == "start":
#             self._state = "nonce"
#             msg = message.query(
#                 0,
#                 "%s.$cmd" % self.pool._db_name,
#                 0,
#                 1,
#                 SON({'getnonce': 1}),
#                 SON({})
#             )
#             self.connection._send_message(msg, self.process)
#         elif self._state == "nonce":
#             # this is the nonce response
#             self._state = "finish"
#             try:
#                 nonce = response['data'][0]['nonce']
#                 key = helpers._auth_key(nonce, self.dbuser, self.dbpass)
#             except Exception as e:
#                 self._error(AuthenticationError(e))
#                 return
#
#             msg = message.query(
#                 0,
#                 "%s.$cmd" % self.pool._db_name,
#                 0,
#                 1,
#                 SON([('authenticate', 1),
#                      ('user', self.dbuser),
#                      ('nonce', nonce),
#                      ('key', key)]),
#                 SON({})
#             )
#             self.connection._send_message(msg, self.process)
#         elif self._state == "finish":
#             self._state = "done"
#             try:
#                 assert response['number_returned'] == 1
#                 response = response['data'][0]
#             except Exception as e:
#                 self._error(AuthenticationError(e))
#                 return
#
#             if response.get("ok") != 1:
#                 self._error(AuthenticationError(response.get("errmsg")))
#                 return
#             self.connection._next_job()
#         else:
#             self._error(ValueError("Unexpected state: %s" % self._state))
#
#
# class ConnectRSJob(AsyncJob):
#
#     def __init__(self, connection, seed, rs, secondary_only, err_callback):
#         super(ConnectRSJob, self).__init__(connection, "seed", err_callback)
#         self.known_hosts = set(seed)
#         self.rs = rs
#         self._blacklisted = set()
#         self._primary = None
#         self._sec_only = secondary_only
#
#     def process(self, response=None, error=None):
#         if error:
#             if self._state == "ismaster":
#                 self._state = "seed"
#
#         if self._state == "seed":
#             if self._sec_only and self._primary:
#                 # Add primary host to blacklisted to avoid connecting to it
#                 self._blacklisted.add(self._primary)
#
#             fresh = self.known_hosts ^ self._blacklisted
#
#             while fresh:
#                 if self._primary and self._primary not in self._blacklisted:
#                     # Try primary first
#                     h = self._primary
#                 else:
#                     h = random.choice(list(fresh))
#
#                 if h in fresh:
#                     fresh.remove(h)
#
#                 # Add tried host to blacklisted
#                 self._blacklisted.add(h)
#
#                 self.connection._host, self.connection._port = h
#                 try:
#                     self.connection._socket_connect()
#                 except InterfaceError as e:
#                     pass
#                     #logging.error("Failed to connect to the host: %s", e)
#                 else:
#                     break
#
#             else:
#                 self._error(RSConnectionError("No more hosts to try, tried: %s" % self.known_hosts))
#                 return
#
#             self._state = "ismaster"
#             msg = message.query(
#                 options=0,
#                 collection_name="admin.$cmd",
#                 num_to_skip=0,
#                 num_to_return=-1,
#                 query=SON([("ismaster", 1)])
#             )
#             self.connection._send_message(msg, self.process)
#
#         elif self._state == "ismaster":
#             try:
#                 res = response["data"][0]
#             except Exception as e:
#                 self._error(RSConnectionError("Invalid response data: %r" % response.get("data")))
#                 return
#
#             rs_name = res.get("setName")
#             if rs_name and rs_name != self.rs:
#                 self._error(RSConnectionError("Wrong replica set: %s, expected: %s" % (rs_name, self.rs)))
#                 return
#
#             hosts = res.get("hosts")
#             if hosts:
#                 self.known_hosts.update(helpers._parse_host(h) for h in hosts)
#
#             ismaster = res.get("ismaster")
#             hidden = res.get("hidden")
#             try:
#                 if ismaster and not self._sec_only:  # master and required to connect to primary
#                     self._state = "done"
#                     self.connection._next_job()
#                 elif not ismaster and self._sec_only and not hidden:  # not master and required to connect to secondary
#                     self._state = "done"
#                     self.connection._next_job()
#                 else:  # either not master and primary connection required or master and secondary required
#                     primary = res.get("primary")
#                     if primary:
#                         self._primary = helpers._parse_host(primary)
#                     self._state = "seed"
#                     self.process()
#             except Exception as e:
#                 self._error(RSConnectionError(e))
#                 return
