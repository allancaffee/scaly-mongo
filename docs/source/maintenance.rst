Maintenance
===========

Indexes
-------

Generating well formed documents is useful, but without indexes efficient
lookups are all but impossible.  ScalyMongo provides a declarative syntax for
describing collection indexes.  ScalyMongo uses this information to check for
things like poorly sharded queries and unique indexes that cannot be enforced.

The indexes themselves though are not created automatically.  The task of index
creation should be considered an administrative task and should not be
automatically done during runtime for several reasons:

* Foreground index creation `blocks other database actions
  <http://www.mongodb.org/display/DOCS/Indexes#Indexes-BackgroundIndexCreation>`_.

* Even if the new indexes are created in the background they will not be
  immediately available for any newly deployed code that relies on them for
  reasonable performance.

* Although creating an index in the background does not block other clients
  from reading and writing to a collection it *does* block the client creating
  the index.  See `Indexing as a Background Operation`_ for more information.

* Creating new indexes is not guaranteed to succeed.  For example creating a
  new unique index without specifying `drop_dups` will fail in the event that
  duplicate records are already present.

.. _Indexing as a Background Operation: http://www.mongodb.org/display/DOCS/Indexing+as+a+Background+Operation


So, if ScalyMongo doesn't automatically set up indexes, how does one go about
creating indexes?


Creating Indexes with ``scalymongo-ensure-indexes``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.1.4
    ScalyMongo now comes with a utility script called
    ``scalymongo-ensure-indexes`` to create indexes.

This script requires two arguments:
    * The name of the module containing your project's model classes.
    * A MongoDB endpoint to connect to.

For example if your models are defined in (or imported by) ``myproject.models``
and your MongoDB server is running at ``mongo.example.com``, you can create the
indexes described in your model by running:

.. code-block:: sh

    $ scalymongo-ensure-indexes myproject.models mongodb://mongo.example.com

For details on additional options that are available for creating indexes
please refer to the output of ``scalymongo-ensure-indexes --help``.

.. note::
    This administrative script should be run *before* deploying any code which
    depends on the indexes.


Creating Indexes with Earlier Versions of ScalyMongo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Projects using versions of ScalyMongo prior to 0.1.4 can create indexes with a
short script like the one presented below:

.. code-block:: python

    from scalymongo import Connection

    # Import the models so that they get registered with Connection.
    import myproject.models


    connection = Connection()
    for model in connection.models:
        model.ensure_indexes(background=True)

Notice that the script creates indexes in the background.  This prevents the
operation from blocking other reads and writes on the collection, but also
means that index creation will take longer.
