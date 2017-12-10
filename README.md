# mokito
An asynchronous ORM for accessing MongoDB in Tornado

## What is mokito?
(MOngodb + KIt + TOrnado) is an asynchronous toolkit for working with ``mongodb`` inside a ``tornado`` app, like ``mongokit``. Mokito has a pure implementation of python + tornado and only depends on tornado and bson (provided by pymongo)

## Why not pymongo?
[PyMongo](http://api.mongodb.org/python/current/) is the recommended way to work with MongoDB in Python, but isn't asynchronous and not run inside tornado's IOLoop. If you use pymongo you won't take the advantages of tornado.

## Features
* validation and conversion of data to the specified type
* support for unstructured data
* dot notation
* control over data presentation
* control over data validation
* mapping onto the same document of models with different schemes

## Installing
```bash
pip install pymomgo tornado motor pytz python-dateutil
pip install mokito
```

## A quick example
```python
import motor
import mokito
 
MONGO_URI = 'mongodb://127.0.0.1:27017'
MONGO_DB = 'foo'
 
 
class BaseDocument(mokito.Document):
    __database__ = motor.motor_tornado.MotorClient(MONGO_URI)[MONGO_DB]
 
 
class Author(BaseDocument):
    scheme = {
        'name':{
            'first': str,
            'last': str
        },
        'age': int,
        'mail': str
    }
 
 
class Blog(mokito.Model):
    scheme = {
        'title':str
    }
 
 
class Post(BaseDocument):
    __collection__ = 'blog_post'
    scheme = {
        'blog': Blog,
        'post': str,
        'author': Author
    }
 

async def example():
    alice = Author({'name': {'first': 'Alice'}, 'mail': 'alice@google.com'})
    await alice.save()
    
    post = Post()
    post['blog.title'].value = 'My blob'
    post['post'].value = 'My post'
    post['author'] = alice
    await post.save()
```
MongoDB in the collection "author" will write this document:
```javascript
{"_id": ObjectId("..."), "name": {"first": "Alice"}, "mail": "alice@google.com"}
```
and in the collection "blog_post" will write this document:
```javascript
{"_id": ObjectId("..."), "blog": {"title": "My blob"}, "post": "My post", "author": DBRef("author", ObjectId("..."))}
```


Please see the [wiki](https://github.com/asmodius/mokito/wiki) for more examples.
