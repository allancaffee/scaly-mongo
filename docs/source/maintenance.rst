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
creating indexes?  Projects using ScalyMongo should have an administrative
script which generates the indexes for all applicable collections.  This script
would look much like the example below:

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

.. note::
    This administrative script should be run *before* deploying any code which
    depends on the indexes.

In upcoming versions a general version of this script will be provided with
ScalyMongo to simplify the process of index creation.
