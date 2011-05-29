"""The base document models.
"""

from scalymongo.errors import UnsafeBehaviorError
from scalymongo.schema import SchemaDocument, SchemaMetaclass


class DocumentMetaclass(SchemaMetaclass):
    """This metaclass records all concrete :class:`Document` types.
    """

    concrete_classes = set()

    def __new__(cls, name, bases, attrs):
        rv = SchemaMetaclass.__new__(cls, name, bases, attrs)
        if not attrs.get('abstract', False):
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
