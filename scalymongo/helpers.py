
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
