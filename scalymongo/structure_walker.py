"""
Structure Walker
================

A utility used to aid in structure validation.

"""
from inspect import isclass

from scalymongo.errors import ValidationError


class StructureWalker(object):
    """A helper class to recurse a :class:`dict`-like object in accordance with
    a structure.

    :param field_translator: should be function mapping the ``value`` and
        ``type_`` to the new value for a key.

    """

    def __init__(self, field_validator):
        self.field_validator = field_validator

    def walk_dict(self, body, structure, path=None):
        """Validate a dictionary in accordance with `structure`.

        A :class:`ValidationError` is raised if any fields in `body` are
        not present in `structure`.

        """
        _check_for_unknown_fields(body, structure, path)

        for field, sub_structure in structure.iteritems():
            if isclass(field):
                field_type = field
                # For structures like {<TYPE>: {<STRUCT>}} iterate values
                # in the body with keys of <TYPE> and verify each against
                # <STRUCT>.
                for key, value in body.iteritems():
                    if isinstance(key, field_type):
                        self._recurse_or_validate_field(
                            value, sub_structure, _join(path, key))

            if field in body:
                self._recurse_or_validate_field(
                    body[field], sub_structure, _join(path, field))

    def _recurse_or_validate_field(self, value, sub_structure, path):
        if isinstance(sub_structure, list):
            assert len(sub_structure) == 1
            if isinstance(value, dict):
                # If the structure is a dict this is fine so long as all of the
                # keys are integers or the positional operator (`$`). This
                # happens with the $set update modifier since we expand
                # {'foo.0.bar': 1} to {'foo': {'0': {'bar': 1}}}
                for key, value in value.iteritems():
                    assert key.isdigit() or key == '$'
                    self._recurse_or_validate_field(
                        value, sub_structure[0], _join(path, key))
            else:
                # Validate each value in the list against the specified content
                # type.
                for i, value in enumerate(value):
                    self._recurse_or_validate_field(
                        value, sub_structure[0], _join(path, i))
            return

        if isinstance(sub_structure, dict):
            self.walk_dict(value, sub_structure, path)
            return

        self.field_validator(path, value, sub_structure)


def _check_for_unknown_fields(body, structure, path):
    """Check `body` for any keys not present in `structure`.

    This only checks the first level of keys.  Any keys from :class:`dict`s in
    the `body`\ 's values will not be checked.

    """
    type_keys = tuple([key for key in structure if isclass(key)])
    existing_fields = set([key for key in body if not isclass(key)])
    unknown_fields = existing_fields.difference(structure.keys())
    # If there are valid types for a key filter out unknown fields that match a
    # type.
    if type_keys:
        unknown_fields = [key for key in unknown_fields
                          if not isinstance(key, type_keys)]

    if unknown_fields:
        unknown_fields = ', '.join([repr(field) for field in unknown_fields])
        if path:
            err = ('Encountered field(s), in subdocument at {0},'
                   ' not present in structure: {1}'.format(
                       path, unknown_fields))
        else:
            err = 'Encountered field(s) not present in structure: {0}'.format(
                unknown_fields)

        raise ValidationError(err)


def _join(head, tail):
    """Join `head` and `tail` with a dot.

    If head is ``None`` only `tail` is returned.

    """
    if head is None:
        return tail
    return '{0}.{1}'.format(head, tail)
