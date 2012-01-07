"""
Errors
======

Exceptions that can be raised by ScalyMongo.

"""


class UnsafeBehaviorError(Exception):
    """Raised when ScalyMongo detects behavior that might not be safe.

    This exception is used to notify developers when a particular action may
    cause unsafe behavior in their application.  For example calling
    :meth:`~scalymongo.document.Document.save` on a model that has already been
    written to Mongo will raise this exception by default to warn developers
    that doing so will overwrite any changes made to that document since it was
    last loaded or saved.

    """
    pass


class GlobalQueryException(Exception):
    """Raised when a query will hit multiple shards.

    This exception is raised by default when doing a
    :meth:`~scalymongo.document.Document.find`,
    :meth:`~scalymongo.document.Document.remove` or any other type of query
    when the query is likely to hit multiple shards.  This check is done in
    order to warn developers of behavior that may not perform well at scale.

    """
    pass


class SchemaError(ValueError):
    """Raised when a ScalyMongo model has an invalid schema.

    Examples of invalid schemas are:

    - Unique indexes which cannot be enforced due to sharding.
    - Multiple shard keys on a single document type.

    """
    pass


class ValidationError(Exception):
    """Raised when a model has failed validation."""
    pass


class ModifyFailedError(Exception):
    """Raised when :meth:`~scalymongo.document.Document.modify` fails."""
    pass
