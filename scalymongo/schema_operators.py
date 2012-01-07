class OR(object):
    """Specify that a value should be one of several types."""

    def __init__(self, *args):
        self.valid_types = tuple(sorted(args))

    def evaluate(self, value):
        """Determine if `value` meets this operator's criteria."""
        return isinstance(value, self.valid_types)

    def __eq__(self, other):
        """An equality predicate to simplify unit testing."""
        if not hasattr(other, 'valid_types'):
            return False
        return self.valid_types == other.valid_types

    def __repr__(self):
        return '<OR {0}>'.format(', '.join([repr(x) for x in self.valid_types]))


class IS(object):
    """Specify that a value should one of several *exact values*.

    This operator uses a :class:`set` for fast checking so any values must be
    hashable.

    """

    def __init__(self, *args):
        self.valid_values = set(args)

    def evaluate(self, value):
        """Determine if `value` meets this operator's criteria."""
        return value in self.valid_values

    def __eq__(self, other):
        """An equality predicate to simplify unit testing."""
        if not hasattr(other, 'valid_values'):
            return False
        return self.valid_values == other.valid_values

    def __repr__(self):
        return '<IS {0}>'.format(', '.join([repr(x) for x in self.valid_values]))
