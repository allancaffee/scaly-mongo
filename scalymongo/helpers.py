"""
Helpers
=======

Useful functions and classes that don't really fit elsewhere.

"""


def is_update_modifier(doc):
    """Return true if and only if `doc` is an update modifier.

    This function only checks the first key it finds.  `doc` is assumed to
    be either a valid update modifier or a replacement document.  The result of
    passing a bad modifier or document is undefined.

    """
    if not doc:
        return False

    # To save time just check the first key.
    key = doc.iterkeys().next()
    return key.startswith('$')


def value_or_result(potential):
    """Return `potential` or its return value.

    If `potential` is callable then the result of calling it without arguments
    is returned instead.

    """
    if callable(potential):
        return potential()
    return potential


class ClassDefault(object):
    """A sentinel value signaling that the class default should be used.

    This is used as default value for keyword arguments so that a default can
    be set during class declaration, but the value can still be explicitly
    specified when the function is called.

    """


class ConversionDict(dict):
    """A :class:`dict` subclass that wraps contents on lookup.

    >>> cd = ConversionDict({'x': 5, 'y': 6}, {'x': str})
    >>> cd['x']
    '5'
    >>> cd.x
    '5'
    >>> cd['y']
    6
    >>> cd.y
    6

    :param content: is the dictionary content.
    :param conversions: is a dictionary containing conversions to be applied on
        lookup.  If no conversion is present in `conversions` the value is
        returned unchanged.

    """

    NONKEY_ATTRS = set(['_conversions'])
    """Attributes which should not be treated as keys in the dictionary.

    Classes extending :class:`ConversionDict` should add the names of any
    attributes they wish to keep that should not be set into the underlying
    :class:`dict`.

    """

    def __init__(self, content, conversions):
        dict.__init__(self, content)
        self._conversions = conversions

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        conversion = self.__get_conversion(key)
        return self.__convert_value(value, conversion)

    @staticmethod
    def __convert_value(value, conversion):
        """Convert `value` using `conversion`.

        If `conversion` is ``None`` then `value` is returned unchanged.

        """
        if conversion is None:
            return value

        if isinstance(conversion, dict):
            return ConversionDict(value, conversion)

        if isinstance(value, list):
            return [conversion(x) for x in value]

        return conversion(value)

    def __get_conversion(self, key):
        if self._conversions:
            return self._conversions.get(key)

    def __getattr__(self, name):
        """Get the `name` attribute.

        If `name` is a :class:`dict` then it will be wrapped in a new
        :class:`ConversionDict`.  This allows chained dot notation to reference
        items in embedded dictionaries.

        """
        if name in self:
            return self.__getitem__(name)

        raise AttributeError('{0.__name__!r} has no attribute {1!r}.'.format(
            type(self), name))

    def __setattr__(self, name, value):
        """Set an attribute.

        Put an item in this dictionary unless `name` is a contained in
        :data:`NONKEY_ATTRS`.  Or some other attribute already set on either
        the instance or the class (which allows the tests to dingus out methods
        on instances).

        """
        if name in self.NONKEY_ATTRS or name in dir(self):
            object.__setattr__(self, name, value)
        else:
            self.__setitem__(name, value)

    def iteritems(self):
        """Iterate the items in this :class:`ConversionDict`.

        The underlying :meth:`dict.iteritems` must be wrapped such that the
        values returned by this generator are converted to appropriate types.

        """
        for key, value in dict.iteritems(self):
            conversion = self.__get_conversion(key)
            yield key, self.__convert_value(value, conversion)

    def itervalues(self):
        """Iterate the values in this :class:`ConversionDict`.

        The values are converted to the appropriate type before returning.

        """
        for key, value in self.iteritems():
            yield value

    def items(self):
        """Return a list of the items in this :class:`ConversionDict`."""
        return [item for item in self.iteritems()]

    def values(self):
        """Return a list of the values in this :class:`ConversionDict`."""
        return [value for value in self.itervalues()]
