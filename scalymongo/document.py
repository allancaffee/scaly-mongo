"""The base document models.
"""

from scalymongo.errors import UnsafeBehaviorError
from scalymongo.schema import SchemaDocument, SchemaMetaclass


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
    def find_one(cls, spec=None, **kwargs):
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
        return cls.collection.find_one(spec, **kwargs)

    @classmethod
    def find(cls, spec=None, *args, **kwargs):
        """Query the database for documents of this type.

        This is a wrapped call to :meth:`pymongo.collection.Collection.find`
        which returns document objects of the appropriate class instead of
        ``dict`` instances.
        """
        kwargs['as_class'] = cls
        return cls.collection.find(spec, *args, **kwargs)
