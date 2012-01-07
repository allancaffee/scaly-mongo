"""
Document
========

The base document models.

"""
import functools

from pymongo.errors import OperationFailure

from scalymongo.cursor import Cursor
from scalymongo.errors import (
    GlobalQueryException,
    ModifyFailedError,
    UnsafeBehaviorError,
)
from scalymongo.helpers import (
    ClassDefault,
    is_update_modifier,
    value_or_result,
)
from scalymongo.schema import (
    SchemaDocument,
    SchemaMetaclass,
    validate_update_modifier,
)


class DocumentMetaclass(SchemaMetaclass):
    """This metaclass records all concrete :class:`Document` types.

    This excludes classes created by
    :meth:`~scalymongo.connection.Connection.connect_document`.

    """

    concrete_classes = set()

    def __new__(cls, name, bases, attrs):
        rv = SchemaMetaclass.__new__(cls, name, bases, attrs)
        attrs['abstract'] = attrs.get('abstract', False)
        if not attrs['abstract'] and not attrs.get('connection'):
            cls.concrete_classes.add(rv)
        return rv


def get_concrete_classes():
    """Return a set of all non-abstract :class:`Document` subclasses."""
    return DocumentMetaclass.concrete_classes


class Document(SchemaDocument):
    """The base document class all user models should extend.

    Any subclasses of :class:`Document` which are not abstract can be used from
    the model property on a :class:`~scalymongo.connection.Connection`.  This
    class wraps many of the methods available on
    :class:`pymongo.collection.Collection` in order to return objects of the
    appropriate subclass.

    """

    __metaclass__ = DocumentMetaclass
    abstract = True
    default_values = {}
    """A dictionary mapping fields to default values.

    The values may either be static values or a function that returns a default
    value.  For example to put a new :class:`~uuid.UUID` in the field `uuid`
    you would use a default like:

    .. code-block:: python

        default_values = {'uuid': uuid.UUID}

    """
    safe_insert = True
    """A :class:`bool` indicating whether :meth:`save` should default to safe insertion.

    This defaults to ``True`` but may be overridden by subclasses.

    """

    def __init__(self, *args, **kwargs):
        SchemaDocument.__init__(self, *args, **kwargs)
        for key, value in self.default_values.iteritems():
            self.setdefault(key, value_or_result(value))

    def save(self, safe=ClassDefault, **kwargs):
        """Save this document.

        If this document has already been saved an :class:`UnsafeBehaviorError`
        will be raised.  The document will be validated before saving.

        :keyword safe: Corresponds to the `safe` keyword of the underlying
            function.  If not specified this defaults to using the
            :data:`safe_insert` attribute.  (Which in turn is set to ``True``
            on the :class:`Document`.

        All additional keyword arguments will be passed to
        :meth:`pymongo.collection.Collection.save`.

        """
        if '_id' in self:
            raise UnsafeBehaviorError(
                'This document has already been saved once.'
                ' Further alterations should use modify.')

        if safe is ClassDefault:
            safe = self.safe_insert

        self.validate()
        self.collection.save(self, safe=safe, **kwargs)

    def reload(self):
        """Reload this document.

        This will make use of the shard key for sharded collections to avoid a
        global query.

        """
        spec = self.shard_key
        spec['_id'] = self['_id']
        # Call the parent `update` not the classmethod.
        SchemaDocument.update(self, self.find_one(spec))

    def modify(self, update, query=None):
        """Modify this document using :meth:`find_and_modify`.

        If the document could not be updated a
        :class:`~scalymongo.errors.ModifyFailedError` is raised.  This is
        usually caused by the document not being found on the server (e.g. it
        was deleted or does not match the specified `query`).

        :param update: Is an update modifier or replacement document to be
            be used for this

        :param query: A query specification for any additional parameters to
            be used in the :meth:`find_and_modify` query.  This document's
            ``_id`` field and it's shard key fields (where applicable) are
            included in addition to any parameters specified in the
            `query`.

        """
        full_query = self.shard_key
        if query:
            full_query.update(query)
        full_query['_id'] = self['_id']
        result = self.find_and_modify(full_query, update, new=True)
        if result is None:
            self.reload()
            raise ModifyFailedError(
                'Failed to update document.  The document was not found'
                ' based on the criteria {0}.  Document was {1}.'.format(
                query, self),
            )
        # We have to clear the existing dictionary first in case the operation
        # included an `$unset` or replaced the entire document.
        self.clear()
        # Call the parent `update` not the classmethod.
        SchemaDocument.update(self, result)

    @classmethod
    def ensure_indexes(cls, **kwargs):
        """Ensure this any indexes declared on this index :class:`Document`.

        This is an administrative task and should be done with care as
        (re)building large indexes can make a database unusable for some time.
        Any additional `kwargs` are passed to
        :meth:`pymongo.collection.Collection.ensure_index`.

        """
        for index in cls.indexes:
            kwargs['unique'] = index.get('unique', False)
            cls.collection.ensure_index(index['fields'], **kwargs)

    @classmethod
    def find_one(cls, spec=None, allow_global=False, **kwargs):
        """Find and return one matching document of this type.

        :param spec: (optional): Is a query to find the matching document.
          Note that unlike other tools providing `find_one` scalymongo requires
          this value to be a dictionary including at a bare minimum the shard
          key for this models collection.

        :param kwargs: (optional): Additional keyword arguments will be
          passed to :meth:`pymongo.collection.Collection.find_one`.

        """
        if not allow_global:
            cls.check_query_sharding(spec)
        result = cls.collection.find_one(spec, **kwargs)
        if result is not None:
            return cls(result)

    @classmethod
    def find(cls, spec=None, allow_global=False, *args, **kwargs):
        """Query the database for documents of this type.

        This is a wrapped call to :meth:`pymongo.collection.Collection.find`
        which returns document objects of the appropriate class instead of
        ``dict`` instances.  All additional arguments are passed to the
        underlying method.

        """
        if not allow_global:
            cls.check_query_sharding(spec)
        result = cls.collection.find(spec, *args, **kwargs)
        return Cursor(result, cls)

    @classmethod
    def find_and_modify(cls, query={}, update=None,
                        allow_global=False, **kwargs):
        """Find and atomically update a single document.

        .. note::
            This method returns the *old* (pre-update) version of the document
            by default.  This is the default for ``findAndModify`` in the Mongo
            shell and it is maintained here for the sake of consistency.  Pass
            `new` as ``True`` to return the updated document instead.

        :param query: filter for the update (default ``{}``)
        :param update: see second argument to :meth:`update` (no default)
        :keyword allow_global: If ``True`` the query will not be checked to
            ensure that it contains the full shard key.  (default ``False``)
        :param sort: priority if multiple objects match (default ``{}``)
        :param remove: remove rather than updating (default ``False``)
        :param new: return updated rather than original object
            (default ``False``)
        :param fields: see second argument to :meth:`find` (default all)
        :param upsert: insert if object doesn't exist (default ``False``)
        :param kwargs: any other options the findAndModify_ command
            supports can be passed here.

        .. _findAndModify: http://www.mongodb.org/display/DOCS/findAndModify+Command

        """
        if not allow_global:
            cls.check_query_sharding(query)

        cls._validate_update(update)

        try:
            # Use the `command` operation since `find_and_modify` is only
            # available in pymongo>=1.10.
            returned = cls.database.command(
                'findandmodify', cls.collection.name,
                query=query, update=update, **kwargs)
        except OperationFailure:
            return None

        if returned['value'] is None:
            return None

        return cls(returned['value'])

    @classmethod
    def update(cls, spec, document, allow_global=False, **kwargs):
        """Update a document matching `spec` using `document`.

        Additional keyword arguments are passed to
        :meth:`pymongo.collection.Collection.update`.

        :param spec: is a document specification (i.e. query) for the document
            to be updated.  if more than one document matches only the first
            will but updated unless `multi` is ``True``.
        :param document: is expected to be either a new document or an update
            modifier.
        :keyword multi: update multiple documents or just the first (default
            ``False``).

        """
        if not allow_global:
            cls.check_query_sharding(spec)

        cls._validate_update(document)

        return cls.collection.update(spec, document, **kwargs)

    @classmethod
    def remove(cls, spec, allow_global=False, **kwargs):
        """Find and remove documents matching `spec`.

        Additional keywords are passed to
        :meth:`pymongo.collection.Collection.remove`.

        """
        if not allow_global:
            cls.check_query_sharding(spec)

        return cls.collection.remove(spec, **kwargs)

    @classmethod
    def _validate_update(cls, document):
        """Validate an update described in `document`.

        :param document: is expected to be either a new document or an update
            modifier.

        """
        if is_update_modifier(document):
            validate_update_modifier(document, cls.structure)
        else:
            # It's a full document replace.
            cls(document).validate()

    @classmethod
    def check_query_sharding(cls, spec):
        """Check that all required keys are present in `spec`.

        If any shard keys are unspecified this will raise a
        :class:`GlobalQueryException`.

        """
        if cls.shard_index:
            keys = set(cls.shard_index['fields'])
            missing_keys = keys.difference(spec.keys())
            if missing_keys:
                raise GlobalQueryException(
                    'Some or all of the shard key was not specified.  Missing'
                    ' fields were {0}.'.format(
                        ', '.join([key for key in missing_keys])))

    @property
    def shard_key(self):
        if not self.shard_index:
            return {}
        key_dict = {}
        for key in self.shard_index['fields']:
            key_dict[key] = self[key]
        return key_dict
