"""The base document models.
"""
import functools

from pymongo.errors import OperationFailure

from scalymongo.errors import UnsafeBehaviorError, GlobalQueryException
from scalymongo.helpers import is_update_modifier
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
        if not attrs.get('abstract', False) and not attrs.get('connection'):
            cls.concrete_classes.add(rv)
        return rv


def get_concrete_classes():
    """Return a set of all registered :class:`Document` classes."""
    return DocumentMetaclass.concrete_classes


class Document(SchemaDocument):

    __metaclass__ = DocumentMetaclass
    abstract = True

    def save(self):
        if '_id' in self:
            raise UnsafeBehaviorError(
                'This document has already been saved once.'
                ' Further alterations should use modify.')

        self.validate()
        self.collection.insert(self)

    def reload(self):
        """Reload this document.

        Make use of the shard key for sharded collections to avoid a gloabl
        query.
        """
        spec = self.shard_key
        spec['_id'] = self['_id']
        # Call the parent `update` not the classmethod.
        SchemaDocument.update(self, self.find_one(spec))

    @classmethod
    def ensure_indexes(cls, **kwargs):
        """Ensure this any indexes declared on this index :class:`Document`.

        This is an administrative task and should be done with care as
        (re)building large indexes can make a database unusable for some time.
        """
        for index in cls.indexes:
            kwargs['unique'] = index.get('unique', False)
            cls.collection.ensure_index(index['fields'], **kwargs)

    @classmethod
    def find_one(cls, spec=None, allow_global=False, **kwargs):
        """Find and return one matching document of this type.

        :Parameters:

        - :param:`spec` (optional): Is a query to find the matching document.
          Note that unlike other tools providing `find_one` scalymongo requires
          this value to be a dictionary including at a bare minimum the shard
          key for this models collection.

        - :param:`kwargs` (optional): Additional keyword arguments will be
          passed to :meth:`pymongo.collection.Collection.find_one`.
        """
        kwargs['as_class'] = cls
        if not allow_global:
            cls.check_query_sharding(spec)
        return cls.collection.find_one(spec, **kwargs)

    @classmethod
    def find(cls, spec=None, allow_global=False, *args, **kwargs):
        """Query the database for documents of this type.

        This is a wrapped call to :meth:`pymongo.collection.Collection.find`
        which returns document objects of the appropriate class instead of
        ``dict`` instances.
        """
        kwargs['as_class'] = cls
        if not allow_global:
            cls.check_query_sharding(spec)
        return cls.collection.find(spec, *args, **kwargs)

    @classmethod
    def find_and_modify(cls, query={}, update=None,
                        allow_global=False, **kwargs):
        """Find and atomically update a single document.

        Note that this method returns *old* (pre-update) version of the document
        by default.  This is the default for 'findAndModify' in the Mongo shell
        and it is maintained here for the sake of consistency.  Pass :keyword
        new: as ``True`` to return the updated document instead.

        :Parameters:
            - `query`: filter for the update (default ``{}``)
            - `sort`: priority if multiple objects match (default ``{}``)
            - `update`: see second argument to :meth:`update` (no default)
            - `remove`: remove rather than updating (default ``False``)
            - `new`: return updated rather than original object
              (default ``False``)
            - `fields`: see second argument to :meth:`find` (default all)
            - `upsert`: insert if object doesn't exist (default ``False``)
            - `**kwargs`: any other options the findAndModify_ command
              supports can be passed here.
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

        return cls(returned['value'])

    @classmethod
    def update(cls, spec, document, allow_global=False, **kwargs):
        """Update a document matching :param spec: using :param document:.

        :param document: is expected to be either a new document or an update
        modifier.
        """
        if not allow_global:
            cls.check_query_sharding(spec)

        cls._validate_update(document)

        return cls.collection.update(spec, document, **kwargs)

    @classmethod
    def _validate_update(cls, document):
        """Validate an update described in :param document:.

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
        """Check that all required keys are present in :param spec:.

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
