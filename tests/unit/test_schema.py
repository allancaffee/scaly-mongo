# -*- coding: utf-8 -*-
import datetime

from dingus import Dingus, DingusTestCase, DontCare
from nose.tools import assert_raises

from scalymongo.schema import *
import scalymongo.schema as mod


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


class DescribeUpdatingListClass(object):

    def should_extend_list(self):
        assert issubclass(UpdatingList, list)

    def should_implement_update_as_list_extend(self):
        assert UpdatingList.update is list.extend


class DescribeSchemaMetaclassTypeClass(object):

    def should_have_structure_as_dict(self):
        assert SchemaMetaclass.mergeable_attrs['structure'] is dict

    def should_have_indexes_as_set(self):
        assert SchemaMetaclass.mergeable_attrs['indexes'] is UpdatingList

    def should_have_required_fields_as_set(self):
        assert SchemaMetaclass.mergeable_attrs['required_fields'] is set


class BaseDescribeNewSchemaMetaclass(
    DingusTestCase(SchemaMetaclass)):

    def setup(self):
        super(BaseDescribeNewSchemaMetaclass, self).setup()
        mod.type = Dingus('type', __new__=Dingus('__new__'))


class WhenSchemaMetaclassHasBaseClasses(BaseDescribeNewSchemaMetaclass):

    def setup(self):
        BaseDescribeNewSchemaMetaclass.setup(self)
        self.name = Dingus('name')
        self.base_a = Dingus(
            'BaseA',
            structure={'a_1': str, 'a_2': dict},
            indexes=[Dingus('index_a')],
            required_fields=['a_2'],
        )
        self.base_b = Dingus(
            'BaseB',
            structure={'b_1': str, 'b_2': dict},
            indexes=[Dingus('index_b')],
            required_fields=['b_2'],
        )
        self.bases = [self.base_a, self.base_b]
        self.index = Dingus('index')
        self.attrs = {
            'structure': {'c_1': int, 'c_2': float},
            'indexes': [self.index],
            'required_fields': ['c_1', 'c_2'],
        }
        SchemaMetaclass.__new__(SchemaMetaclass, self.name, self.bases, self.attrs)

    def should_merge_attributes(self):
        assert mod.type.__new__.calls(
            '()', SchemaMetaclass, self.name, self.bases, DontCare)

    def should_merge_attr_dict(self):
        attrs = mod.type.__new__.calls('()').once().args[-1]
        assert attrs == {
            'required_fields': set(['a_2', 'b_2', 'c_1', 'c_2']),
            'structure': {'a_1': str, 'a_2': dict,
                          'b_1': str, 'b_2': dict,
                          'c_1': int, 'c_2': float},
            'indexes': [self.index,
                        self.base_a.indexes[0],
                        self.base_b.indexes[0]],
            'shard_index': mod.find_shard_index(),
        }


class BaseFindShardIndex(object):
    pass


class WhenNoShardKeyInIndexes(object):

    def setup(self):
        self.indexes = [
            {'fields': ['foo', 'bar'],
             'unique': True},
            {'fields': 'biz',
             'unique': True},
        ]

        self.returned = find_shard_index(self.indexes)

    def should_return_none(self):
        assert self.returned is None


class WhenMultipleShardKeysInIndex(object):

    def setup(self):
        self.indexes = [
            {'fields': ['foo', 'bar'],
             'unique': True,
             'shard_key': True},
            {'fields': 'biz',
             'unique': True,
             'shard_key': True},
        ]

    def should_raise_schema_error(self):
        assert_raises(SchemaError, find_shard_index, self.indexes)


class WhenMultipleUniquesWithShardKeysInIndex(object):

    def setup(self):
        self.indexes = [
            {'fields': ['foo', 'bar'],
             'unique': True},
            {'fields': 'biz',
             'unique': True,
             'shard_key': True},
        ]

    def should_raise_schema_error(self):
        assert_raises(SchemaError, find_shard_index, self.indexes)


class WhenNonShardKeyIndexIsUnique(object):

    def setup(self):
        self.indexes = [
            {'fields': ['foo', 'bar'],
             'unique': True},
            {'fields': 'biz',
             'shard_key': True},
        ]

    def should_raise_schema_error(self):
        assert_raises(SchemaError, find_shard_index, self.indexes)


class WhenShardKeyExistsAndIsUnique(object):

    def setup(self):
        self.indexes = [
            {'fields': ['foo', 'bar'],
             'unique': True,
             'shard_key': True},
            {'fields': 'biz'}
        ]

        self.returned = find_shard_index(self.indexes)

    def should_return_shard_index(self):
        assert self.returned == {
            'fields': ['foo', 'bar'],
            'unique': True,
            'shard_key': True,
        }


class WhenShardKeyExistsWithNoUniqueIndexes(object):

    def setup(self):
        self.indexes = [
            {'fields': ['foo', 'bar'],
             'shard_key': True},
            {'fields': 'biz'},
        ]

        self.returned = find_shard_index(self.indexes)

    def should_return_shard_index(self):
        assert self.returned == {
            'fields': ['foo', 'bar'],
            'shard_key': True,
        }


class DescribeSchemaDocument(DingusTestCase(SchemaDocument)):

    def setup(self):
        super(DescribeSchemaDocument, self).setup()
        self.document = SchemaDocument()


class WhenValidating(DescribeSchemaDocument):

    def setup(self):
        DescribeSchemaDocument.setup(self)
        self.document.validate()

    def should_validate_structure(self):
        assert mod.validate_structure.calls(
            '()', self.document, self.document.structure)

    def should_validate_required_fields(self):
        assert mod.validate_required_fields.calls(
            '()', self.document, self.document.required_fields)


class DescribeValidateStructure(object):

    def setup(self):
        pass


class WhenSimpleStructureMatchesSimpleFields(DescribeValidateStructure):

    def setup(self):
        DescribeValidateStructure.setup(self)
        self.fields = {'int': 5, 'float': 3.5, 'str': 'string', 'dict': {}}
        self.structure = {'int': int, 'float': float, 'str': str, 'dict': dict}
        validate_structure(self.fields, self.structure)

    def should_not_crash(self):
        pass


class WhenStructureHasEmbeddedDict(DescribeValidateStructure):

    def setup(self):
        DescribeValidateStructure.setup(self)
        self.embedded_fields = {'a': Dingus(), 'b': Dingus()}
        self.embedded_structure = {'a': Dingus(), 'b': Dingus()}
        self.fields = {'int': 5, 'embedded': self.embedded_fields}
        self.structure = {'int': int, 'embedded': self.embedded_structure}
        mod.validate_structure = Dingus('validate_structure')
        validate_structure(self.fields, self.structure)

    def should_recurse_into_embedded_dicts(self):
        assert mod.validate_structure.calls(
            '()', self.embedded_fields, self.embedded_structure)


class BaseFailsValidation(DescribeValidateStructure):

    def should_fail_validation(self):
        assert_raises(ValidationError,
                      validate_structure, self.fields, self.structure)


class WhenFieldsExistButNotInStructure(BaseFailsValidation):

    def setup(self):
        BaseFailsValidation.setup(self)
        self.fields = {'field': Dingus()}
        self.structure = {}


class WhenSimpleStructureDoesntMatchFields(BaseFailsValidation):

    def setup(self):
        BaseFailsValidation.setup(self)
        self.fields = {'int': Dingus(), 'float': 3.5, 'str': 'string'}
        self.structure = {'int': int, 'float': float, 'str': str}


## validate_required_fields ##


class DescribeValidateRequiredFields(
    DingusTestCase(validate_required_fields, ['ValidationError'])):
    pass


class WhenNoRequiredFieldsExists(DescribeValidateRequiredFields):

    def setup(self):
        DescribeValidateRequiredFields.setup(self)
        self.fields = {'a': 1, 'b': 2}
        self.required = set()
        validate_required_fields(self.fields, self.required)

    def should_not_crash(self):
        pass


class WhenAllRequiredFieldsPresent(DescribeValidateRequiredFields):

    def setup(self):
        DescribeValidateRequiredFields.setup(self)
        self.fields = {'a': 1, 'b': 2, 'c': 3}
        self.required = set(['a', 'b'])
        validate_required_fields(self.fields, self.required)

    def should_not_crash(self):
        pass


class WhenMissingARequiredField(DescribeValidateRequiredFields):

    def setup(self):
        DescribeValidateRequiredFields.setup(self)
        self.fields = {'b': 2, 'c': 3}
        self.required = set(['a', 'b'])

    def should_raise_validation_error(self):
        assert_raises(
            ValidationError,
            validate_required_fields, self.fields, self.required)


## validate_update_modifier ##


class WhenSettingValidFieldValue(object):

    def should_not_crash(self):
        validate_update_modifier({'$set': {'field': 1}}, {'field': int})


class WhenSettingInvalidFieldValue(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError,
            "Field 'field' was expected to be an instance of <type 'str'>, but found value 1",
            validate_update_modifier, {'$set': {'field': 1}}, {'field': str})


class WhenUnsettingField(object):

    def should_not_crash(self):
        validate_update_modifier({'$unset': {'field': 1}}, {'field': int})


### $inc modifier ###


class WhenIncrementingIntField(object):

    def should_not_crash(self):
        validate_update_modifier({'$inc': {'field': 1}}, {'field': int})


class WhenIncrementingFloatField(object):

    def should_not_crash(self):
        validate_update_modifier({'$inc': {'field': .5}}, {'field': float})


class WhenIncrementingDatetimeField(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError,
            "Cannot increment non-numeric field of declared as <type 'datetime.datetime'>",
            validate_update_modifier,
            {'$inc': {'field': 1}},
            {'field': datetime.datetime})


### $push modifier ###

class WhenPushingValidValueToDict(object):

    def should_pass_validation(self):
        validate_update_modifier({'$push': {'field': 1}}, {'field': [int]})


class WhenPushingValueToNonListField(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError,
            "Cannot push values onto non-array field of <type 'int'>",
            validate_update_modifier, {'$push': {'field': 1}}, {'field': int})


class WhenPushingValueOfIncorrectTypeOntoListField(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError, "Cannot push value 1 onto array field of type float",
            validate_update_modifier, {'$push': {'field': 1}}, {'field': [float]})


### $pushAll modifier ###


class WhenPushAllingValidValue(object):

    def should_pass_validation(self):
        validate_update_modifier({'$pushAll': {'field': [1, 2]}},
                                 {'field': [int]})


class WhenPushAllingNotListValue(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError,
            "Cannot use modifier $pushAll with non-array argument 1",
            validate_update_modifier,
            {'$pushAll': {'field': 1}},
            {'field': [int]})


class WhenPushAllingArrayOntoNonArrayField(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError,
            "Cannot push values onto non-array field of <type 'int'>",
            validate_update_modifier,
            {'$pushAll': {'field': [1]}},
            {'field': int})


class WhenPushAllingArrayContainingBadValue(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError,
            "Cannot push value 1.1 onto array of <type 'int'>",
            validate_update_modifier,
            {'$pushAll': {'field': [1, 1.1]}},
            {'field': [int]})


### $addToSet modifier ###


class WhenAddToSetingOntoArray(object):

    def should_pass_validation(self):
        validate_update_modifier({'$addToSet': {'field': 1}},
                                 {'field': [int]})


class WhenAddToSetingValueToNonListField(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError,
            "Cannot $addToSet values onto non-array field of <type 'int'>",
            validate_update_modifier, {'$addToSet': {'field': 1}}, {'field': int})


class WhenPushingValueOfIncorrectTypeOntoListField(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError,
            "Cannot $addToSet value 1 onto array of <type 'float'>",
        validate_update_modifier, {'$addToSet': {'field': 1}}, {'field': [float]})


### $rename modifier ###


class WhenRenamingFieldToOneWithIdenticalType(object):

    def should_pass_validation(self):
        validate_update_modifier(
            {'$rename': {'old_field': 'new_field'}},
            {'old_field': [int], 'new_field': [int]})


class WhenRenamingFieldToOneWithDifferentType(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError,
            "Cannot rename field of type [<type 'int'>] to field of type [<type 'float'>]",
            validate_update_modifier,
            {'$rename': {'old_field': 'new_field'}},
            {'old_field': [int], 'new_field': [float]})

### $unknown modifier ###


class WhenUnknownFieldValidatorUsed(object):

    def should_raise_validation_error(self):
        assert_raises_with_message(
            ValidationError, "Encountered unknown update modifier '$unknown'",
            validate_update_modifier,
            {'$unknown': {'field': 1}},
            {'field': int})
