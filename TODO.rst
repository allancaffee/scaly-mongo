Embdedded Documents
===================

Implement support for embedded documents.  For example:

.. code-block:: python

    class Comment(Document):
        structure = {
            'author': basestring,
            'comment': basestring,
            'rank': int,
        }

    class BlogPost(Document):
        structure = {
            'author': basestring,
            'title': basestring,
            'body': basestring,
            'unique_views': int,
            'comments': [Comment]
        }
        __database__ = 'blog'
        __collection__ = 'blog_posts'

In this example the :class:`Comment` documents are stored in MongoDB exactly as
if the underlying ``structure`` had been placed in the ``comments`` list
directly.  The diffence is that ``post['comments']`` returns a list of
:class:`Comment` objects instead of simple `dict` s.


Shard-Friendly DBRefs
=====================

Add a shard friendly replacement for DBRefs_ that can be used to refer to other
objects it a way that they can be queried without hitting all shards.  I'm
thinking about a syntax something like:

.. _DBRefs : http://www.mongodb.org/display/DOCS/Database+References

.. code-block:: python

    class Company(Document):
        structure = {
	    'name': basestring,
	    'address': basestring,
	}
	indexes = {
	    'fields': ['name'],
	    'shard_key': True,
	}
	__database__ = 'test'
	__collection__ = 'companies'

    class User(Document):
        structure = {
	    'name': basestring,
	    'company': ScalyRef(Company),
	}

In the above example the :class:`ScalyRef` would be stored as something like:

..

    {
        'db': 'test',
        'collection': 'companies',
        'keys': {
            '_id': ObjectId('4debbac314dab4a5ec527ba9'),
            'name': '10gen',
        },
    }

This format allows a simple lookup to ensure we can retrieve the document we
want and still make use of shard keys.
