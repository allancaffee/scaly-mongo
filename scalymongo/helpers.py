
def is_update_modifier(doc):
    """Return true if and only if :param doc: is an update modifier.

    This function only checks the first key it finds.  :param doc: is assumed to
    be either a valid update modifier or a replacement document.  The result of
    passing a bad modifier or document is undefined.
    """
    if not doc:
        return False

    # To save time just check the first key.
    key = doc.iterkeys().next()
    return key.startswith('$')


class AttrDict(dict):
    """A ``dict`` whose items can be retrieved as attributes.
    """

    def __getattr__(self, name):
        """Get the :param name: attribute.

        If :param name: is a ``dict`` then it will be wrapped in a new
        :class:`AttrDict`.  This allows chained dot notation to reference
        items in embedded dictionaries.
        """
        if name in self:
            result = self.__getitem__(name)
            if isinstance(result, dict):
                return AttrDict(result)
            return result

        raise AttributeError('{0} has no attribute {1}.'.format(
            repr(type(self).__name__), repr(name)))

    def __setattr__(self, name, value):
        """Set an attribute.

        Put an item in this dictionary unless :param name: is one of the special
        properties ScalyMongo uses.  Or some other attribute already set on
        either the instance or the class (which allows the tests to dingus out
        methods on instances).
        """
        if name in ['collection', 'database', 'connection'] \
               or name in dir(self):
            object.__setattr__(self, name, value)
        else:
            self.__setitem__(name, value)
