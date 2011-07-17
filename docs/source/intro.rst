Introduction
============


Below is simple example of a sharded collection of blog posts

>>> from scalymongo import Document, Connection
>>> class BlogPost(Document):
...     structure = {
...        'author': basestring,
...        'title': basestring,
...        'body': basestring,
...        'unique_views': int,
...        'comments': [{
...            'author': basestring,
...            'comment': basestring,
...            'rank': int,
...        }],
...     }
...     indexes = [{
...         'fields': ['author', 'title'],
...         'shard_key': True,
...         'unique': True,
...     }]
...     __database__ = 'blog'
...     __collection__ = 'blog_posts'
...

The example above describes the structure for a blog post.  Notice that we
declared a unique index on the ``author`` and ``title`` fields.  The index
hasn't actually been created yet, but knowing what indexes exist allow
ScalyMongo to warn you about potentially poor choices in queries.  Also notice
that we declared this index to be used as the shard key.

Now that we've got a simple document class let's create a sample post.

>>> conn = Connection("localhost", 27017)
>>> post = conn.models.BlogPost()
>>> post['author'] = 'Allan'
>>> post['title'] = 'My first post'
>>> post['body'] = "Well, I don't actually have anything to write about..."
>>> post.save()

Great! Now we've got our first blog post.  Now let's look Allan's post up to
make sure it was really saved.

>>> conn.models.BlogPost.find_one({'author': 'Allan'})
Traceback (most recent call last):
  ...
scalymongo.errors.GlobalQueryException: Some or all of the shard key was not specified.  Missing fields were title.

What happended!?  Remember that we declared a shard key on the ``author`` and
``title`` fields?  ScalyMongo noticed that we trying to query without having the
full shard key.  This means that the query might potentially have to hit *every*
shard in our cluster to find the one document we were looking for.  That's
probably not what we wanted to do, and it certainly wouldn't be something we
would want to occur on a regular basis in a production cluster.  Let's refine
our query a bit so that it doesn't hit every shard.

>>> conn.models.BlogPost.find_one({'author': 'Allan', 'title': 'My first post'})
{u'_id': ObjectId('4deb90e41717953527000000'),
 u'author': u'Allan',
 u'body': u"Well, I don't actually have anything to write about...",
 u'title': u'My first post'}

And sure enough that's our first post.  Of course sometimes we *really do* want
to find something even if we don't have the full shard key.  Sometimes this is
useful during development to look up documents from the interactive console.  We
can just override ScalyMongo's recomendations and force the query anyway:

>>> conn.models.BlogPost.find_one({'author': 'Allan'}, allow_global=True)
{u'_id': ObjectId('4deb90e41717953527000000'),
 u'author': u'Allan',
 u'body': u"Well, I don't actually have anything to write about...",
 u'title': u'My first post'}

Take *that* best practices!
