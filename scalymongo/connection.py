"""
Connection
==========

"""
import warnings

import pymongo

from scalymongo.document import get_concrete_classes


class Connection(pymongo.Connection):
    """A connection to a MongoDB database.

    This is a wrapper for a :class:`pymongo.connection.Connection`.

    """

    def connect_document(self, document):
        """Connect a document by creating a new type and injecting the
        connection.

        """
        attrs = {
            'connection': self,
            'database': self[document.__database__],
            'collection': self[document.__database__][document.__collection__],
        }
        return type('Connected{0}'.format(document.__name__),
                    (document,),
                    attrs)

    @property
    def models(self):
        return DocumentProxy(self, get_concrete_classes())


class DocumentProxy(object):
    """A proxy object for accessing or creating :class:`Document` models."""

    def __init__(self, connection, registered):
        self.connection = connection
        self.registered = {}
        for cls in registered:
            if cls.__name__ in self.registered:
                warnings.warn(
                    'Multiple models have been found with the name {0}.'
                    ' The result of connection.models[{0}] will be undefined.'
                    .format(repr(cls.__name__)))
            self.registered[cls.__name__] = cls

    def __getitem__(self, name):
        cls = self._find_document_class(name)
        if not cls:
            raise KeyError('Unknown document {0}'.format(repr(name)))
        return cls

    def __getattr__(self, name):
        cls = self._find_document_class(name)
        if not cls:
            raise AttributeError('Unknown document {0}'.format(repr(name)))
        return cls

    def _find_document_class(self, name):
        cls = self.registered.get(name)
        if not cls:
            return None
        return self.connection.connect_document(cls)

    def __iter__(self):
        """A generator for all models registered on this connection."""
        for value in self.registered.itervalues():
            yield self.connection.connect_document(value)
