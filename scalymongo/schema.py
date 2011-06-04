"""The base document models.
"""

from scalymongo.errors import SchemaError

class UpdatingList(list):
    """Provide a list with an update method.

    Since dicts are used to describe some attributes they must use a data
    structure that does not rely on hashing.  This wrapper class just tacks the
    :meth:`update` method onto a list to make them interoperable with ``set``
    and ``dict`` instances.
    """
    update = list.extend


class SchemaMetaclass(type):
    """Metaclass for documents that have a schema."""

    mergeable_attrs = {
        'structure': dict,
        'indexes': UpdatingList,
        'required_fields': set,
    }
    "Map the merged base class attributes to their expected types."

    def __new__(cls, name, bases, attrs):
        for key, type_ in cls.mergeable_attrs.iteritems():
            if key in attrs:
                attrs[key] = type_(attrs[key])
            else:
                attrs[key] = type_()

        for base in bases:
            for field, type_ in cls.mergeable_attrs.iteritems():
                if hasattr(base, field):
                    attrs[field].update(getattr(base, field))

        attrs['shard_index'] = find_shard_index(attrs['indexes'])

        return type.__new__(cls, name, bases, attrs)


def find_shard_index(indexes):
    """Find the shard key and validate index properties.
    """
    shard_key_indexes = [index for index in indexes
                         if index.get('shard_key')]
    if not shard_key_indexes:
        return None

    if len(shard_key_indexes) > 1:
        raise SchemaError('There can only be one shard key per collection.')

    shard_index = shard_key_indexes[0]

    unique_indexes = [index for index in indexes if index.get('unique')]

    if len(unique_indexes) > 1:
        raise SchemaError(
            'A sharded collection may only have one unique index.')

    if unique_indexes and unique_indexes != shard_key_indexes:
        raise SchemaError(
            'Only the shard key may be used as a unique index on'
            ' a sharded collection.')

    return shard_index


class SchemaDocument(dict):
    """Base class for all documents with an enforced schema."""

    __metaclass__ = SchemaMetaclass

    def validate(self):
        validate_structure(self, self.structure)
        validate_required_fields(self, self.required_fields)


def validate_structure(fields, structure):
    """Recursively validate the structure of a :class:`dict`."""
    for field, value in fields.iteritems():
        if field not in structure:
            raise ValidationError(
                'Encountered unknown field {0}'.format(field))

        expected_type = structure[field]

        # Check the recursive case.
        if type(expected_type) is dict:
            validate_structure(value, expected_type)
        elif not is_field_of_expected_type(value, expected_type):
            raise ValidationError(
                'Field {0} was expected to be an instance of {1},'
                ' but found value {2}'.format(
                    repr(field),
                    repr(expected_type),
                    repr(value)))


def is_field_of_expected_type(value, expected_type):
    """Return ``True`` iff :param value: meets the type description of :param
    expected_type:.

    For now this is a simple :meth:`isinstance` but at some point we want
    mongokit style ``IS``, ``OR``, etc validators.
    """
    return isinstance(value, expected_type)


def validate_required_fields(fields, required):
    """Ensure that all :param required: fields are present in :param fields:.
    """
    missing = required.difference(fields.keys())
    if missing:
        raise ValidationError(
            'Missing required field(s) {0}'.format(
                ','.join([repr(name) for name in missing])))


def validate_update_modifier(spec, structure):
    """Ensure that all operations are valid for the specified structure.
    """
    for modifier, args in spec.iteritems():
        validate_single_modifier(modifier, args, structure)


def validate_single_modifier(modifier, args, structure):
    """Validate a single update modifier.

    :Parameters:
    :param modifier: A single update modifier (e.g. ``$set``).

    :param args: The dictionary of arguments provided to the modifier.

    :param structure: The document structure of the document that the
    modification should be applied to.  This is used to determine whether or not
    the modification is sane for this document.
    """
    if modifier == '$set':
        return validate_structure(args, structure)
    if modifier == '$unset':
        # TODO: Do not allow unsetting required fields or shard_key fields.
        return
    if modifier == '$rename':
        for old_name, new_name in args.iteritems():
            _validate_field_rename(old_name, new_name, structure)
        return

    for field, value in args.iteritems():
        _validate_field_modifier(modifier, structure[field], value)


def _validate_field_rename(old_name, new_name, structure):
    if structure[old_name] != structure[new_name]:
        raise ValidationError(
            'Cannot rename field of type {0} to field of type {1}'.format(
                repr(structure[old_name]), repr(structure[new_name])))


def _validate_field_modifier(modifier, field_type, value):
    # Since $pop, $pull, $pullAll and $bit cannot be used to break a schema
    # (i.e. they can't change the type or add data) adding validation for their
    # content is not a priority.  Perhaps at some point they'll be validated,
    # but for now just let them pass.
    null_validator = lambda field, value: None
    validator = {
        '$inc': _validate_inc_modifier,
        '$push': _validate_push_modifier,
        '$pushAll': _validate_push_all_modifier,
        '$addToSet': _validate_add_to_set_modifier,
        '$pop': null_validator,
        '$pull': null_validator,
        '$pullAll': null_validator,
        '$bit': null_validator,
    }.get(modifier)

    if not validator:
        raise ValidationError(
            'Encountered unknown update modifier {0}'.format(repr(modifier)))

    validator(field_type, value)


def _validate_inc_modifier(field_type, value):
    if field_type not in [int, long, float]:
        raise ValidationError(
            'Cannot increment non-numeric field of declared as {0}'.format(
                repr(field_type)))


def _make_single_value_array_modifier_validator(action_name):
    """Make and return a closure that is a validator for modifiers that add a
    single element to arrays.  I.e $push and $addToSet.
    """
    def _validator(field_type, value):
        if not isinstance(field_type, list):
            raise ValidationError(
                'Cannot {0} values onto non-array field of {1}'.format(
                    action_name, repr(field_type)))

        array_type = field_type[0]
        if not is_field_of_expected_type(value, array_type):
            raise ValidationError(
                'Cannot {0} value {1} onto array of {2}'.format(
                    action_name, repr(value), repr(array_type)))
    return _validator


_validate_push_modifier = _make_single_value_array_modifier_validator('push')
_validate_add_to_set_modifier = _make_single_value_array_modifier_validator('$addToSet')


def _validate_push_all_modifier(field_type, value):
    if not isinstance(value, list):
        raise ValidationError(
            'Cannot use modifier $pushAll with non-array argument {0}'.format(
                value))
    for subvalue in value:
        _validate_push_modifier(field_type, subvalue)


class ValidationError(Exception):
    pass
