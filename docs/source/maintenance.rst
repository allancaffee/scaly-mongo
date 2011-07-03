Maintenance
===========

Generating well formed documents is useful, but without indexes efficient
lookups are all but impossible.  ScalyMongo provides a declarative syntax for
describing collection indexes.  The indexes themselves though are not created
automatically.

Index creation should be considered an administrative task for several reasons:

* Use of indexing has a significant impact on the performance of
  queries. (Yeah, but why does that make it administrative?)

* Foreground index creation blocks all database actions. Indexes_

.. _Indexes: http://www.mongodb.org/display/DOCS/Indexes


Projects using ScalyMongo should have a maintenance script which generates the
indexes for all applicable collections.  This script would look much like the
example below:

.. code-block:: python

    from scalymongo import Connection

    # Import the models so that they get registered with Connection.
    import myproject.models


    connection = Connection()
    for model in connections.models:
        model.ensure_indexes()
