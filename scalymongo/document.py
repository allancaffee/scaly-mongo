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

    @property
    def collection(self):
        return self.database[self.__collection__]

    @property
    def database(self):
        return self.connection[self.__database__]
