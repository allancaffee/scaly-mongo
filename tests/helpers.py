# -*- coding: utf-8 -*-
"""General helpers for tests.
"""

def assert_raises_with_message(
    exception_type, message, function, *args, **kwargs):
    """Assert that a function raises an exception with :param message: as its
    message.
    """
    try:
        function(*args, **kwargs)
    except exception_type as ex:
        if str(ex) != message:
            raise AssertionError(
                'Expected {0} with message of {1}, but message was {2}'
                .format(exception_type.__name__, repr(message), repr(str(ex))))
        return
    raise AssertionError('{0} not raised'.format(exception_type.__name__))
