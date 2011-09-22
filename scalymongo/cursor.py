# -*- coding: utf-8 -*-


class Cursor(object):
    """Wrapper for :class:`pymongo.cursor.Cursor` objects.

    This class is a thin wrapper which takes results returned by the underlying
    cursor and wraps them in the appropriate
    :class:`~scalymongo.document.Document` subclass.
    """

    def __init__(self, wrapped_cursor, document_type):
        self.__wrapped_cursor = wrapped_cursor
        self.__document_type = document_type

    def __getitem__(self, index):
        """Get the item(s) at `index`.

        :param index: may also be a slice.
        """
        returned = self.__wrapped_cursor[index]
        # If the index is a slice then the result is a new cursor with the skip
        # and limit already applied.
        if isinstance(index, slice):
            return Cursor(returned, self.__document_type)
        return self.__document_type(returned)

    def next(self):
        """Return the next document for this cursor.
        """
        return self.__document_type(self.__wrapped_cursor.next())

    def clone(self):
        """Return a new wrapper :class:`Cursor`.
        """
        return Cursor(self.__wrapped_cursor.clone(), self.__document_type)

    def __getattr__(self, attr):
        """All other methods and properties are those of the wrapped cursor.
        """
        return getattr(self.__wrapped_cursor, attr)
