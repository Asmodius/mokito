# mokito
An asynchronous driver and toolkit for accessing MongoDB in Tornado

# What is Mokito?
(MOngodb + mongoKIt + TOrnado) is an asynchronous toolkit for working with ``mongodb`` inside a ``tornado`` app like ``mongokit``. Mokito has a pure implementation of python + tornado and only depends on tornado and bson (provided by pymongo)

## Why not pymongo?
[PyMongo](http://api.mongodb.org/python/current/) is a recommended way to work with MongoDB in python, but isn't asynchronous and not run inside tornado's ioloop. If you use pymongo you won't take the advantages of tornado.

## Why not motor?
[Motor](http://emptysquare.net/motor/) wraps PyMongo and makes it async with greenlet. Is a great project, but it uses greenlet. If you can use greenlets why not use gevent instead of tornado? PyMongo already works with gevent and you dont need to thinking about write all of your code with callbacks. If you are using a very powerfull non-blocking web server with a pure python code, you'll probably want to work with a pure tornado driver for accessing mongo.
