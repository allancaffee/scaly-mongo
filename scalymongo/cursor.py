# -*- coding: utf-8 -*-


def _make_cursor_wrapper_method(method_name):
    """Make a wrapper method for `method_name`.

    `method_name` should be the name of a method on
    :class:`pymongo.cursor.Cursor` which returns another
    :class:`pymongo.cursor.Cursor`.

    The wrapper method will pass along any positional and/or keyword arguments
    to the underlying method of the wrapped cursor and wrap the result in a
    :class:`Cursor` so that it will still yield ScalyMongo documents.

    """
    def _wrapped_method(self, *args, **kwargs):
        method = getattr(self._Cursor__wrapped_cursor, method_name)
        returned = method(*args, **kwargs)
        return Cursor(returned, self._Cursor__document_type)

    return _wrapped_method


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
        """Return the next document for this cursor."""
        return self.__document_type(self.__wrapped_cursor.next())

    def __iter__(self):
        return self

    # Wrap all methods that return a pymongo.cursor.Cursor.
    batch_size = _make_cursor_wrapper_method('batch_size')
    clone = _make_cursor_wrapper_method('clone')
    hint = _make_cursor_wrapper_method('hint')
    limit = _make_cursor_wrapper_method('limit')
    max_scan = _make_cursor_wrapper_method('max_scan')
    rewind = _make_cursor_wrapper_method('rewind')
    skip = _make_cursor_wrapper_method('skip')
    sort = _make_cursor_wrapper_method('sort')
    where = _make_cursor_wrapper_method('where')

    def __getattr__(self, attr):
        """All other methods and properties are those of the wrapped cursor."""
        return getattr(self.__wrapped_cursor, attr)
