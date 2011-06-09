# -*- coding: utf-8 -*-
import datetime

from dingus import Dingus, DingusTestCase, DontCare
from nose.tools import assert_raises

from scalymongo.schema import *
from tests.helpers import assert_raises_with_message
import scalymongo.schema as mod

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
            '_conversions': mod.make_conversion_dict(),
        }


## make_conversion_dict ##

class WhenStructureContainsSchemaDocumentSubclass(object):

    @classmethod
    def setup_class(cls):
        class MySubDoc(SchemaDocument):
            structure = {'foo': int}

        cls.MySubDoc = MySubDoc
        cls.structure = {'bar': MySubDoc}
        cls.result = make_conversion_dict(cls.structure)

    def should_add_conversion(self):
        assert self.result == self.structure


class WhenStructureContainsOnlyPrimatives(object):

    @classmethod
    def setup_class(cls):
        cls.structure = {
            'bar': int,
            'foo': float,
        }
        cls.result = make_conversion_dict(cls.structure)

    def should_have_no_conversions(self):
        assert self.result is None


## find_shard_index ##

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


## DescribeSchemaDocument ##

class DescribeSchemaDocument(DingusTestCase(SchemaDocument)):

    def setup(self):
        super(DescribeSchemaDocument, self).setup()
        class MyDocument(SchemaDocument):
            structure = {'foo': int}
        self.document = MyDocument()


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


## validate_structure ##


class DescribeValidateStructure(DingusTestCase(validate_structure)):

    def setup(self):
        super(DescribeValidateStructure, self).setup()
        self.body = Dingus()
        self.structure = Dingus()
        validate_structure(self.body, self.structure)

    def should_create_structure_walker_with_validate_single_field(self):
        assert mod.StructureWalker.calls('()', mod.validate_single_field)
        assert mod.StructureWalker.calls('()').once()

    def should_validate_document_using_walker(self):
        assert mod.StructureWalker().calls(
            'walk_dict', self.body, self.structure)


## validate_single_field ##


class DescribeValidateSingleField(
    DingusTestCase(validate_single_field, ['ValidationError'])):

    def setup(self):
        super(DescribeValidateSingleField, self).setup()
        self.path = Dingus('path')
        self.value = Dingus('value')
        self.expected_type = Dingus('expected_type')


class WhenFieldIsExpectedType(DescribeValidateSingleField):

    def setup(self):
        DescribeValidateSingleField.setup(self)
        mod.is_field_of_expected_type.return_value = True

    def should_not_crash(self):
        validate_single_field(self.path, self.value, self.expected_type)


class WhenFieldIsNotExpectedType(DescribeValidateSingleField):

    def setup(self):
        DescribeValidateSingleField.setup(self)
        mod.is_field_of_expected_type.return_value = False

    def should_not_crash(self):
        assert_raises_with_message(
            ValidationError,
            'Position <Dingus path> was declared to be <Dingus expected_type>, but encountered value <Dingus value>',
            validate_single_field, self.path, self.value, self.expected_type)


## is_field_of_expected_type ##


class WhenTypeIsSchemaOperator(object):

    def setup(self):
        self.value = Dingus()
        self.expected_type = Dingus()

        self.returned = is_field_of_expected_type(
            self.value, self.expected_type)

    def should_evaluate_value(self):
        assert self.expected_type.calls('evaluate', self.value)

    def should_return_evaluation(self):
        assert self.expected_type.calls('evaluate').once()
        assert self.returned == self.expected_type.evaluate()


class WhenTypeIsSimpleClass(object):

    def should_recognize_matching_instances(self):
        mapping = [
            ('string', str),
            (u'unicode', unicode),
            (1, int),
            (1.1, float),
        ]
        for value, expected_type in mapping:
            assert is_field_of_expected_type(value, expected_type)

    def should_reject_unmatching_instances(self):
        mapping = [
            (u'not string', str),
            ('regular string', unicode),
            (1.1, int),
            (1, float),
            (Dingus(), int),
        ]
        for value, expected_type in mapping:
            assert not is_field_of_expected_type(value, expected_type)


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
            "Position 'field' was declared to be <type 'str'>, but encountered value 1",
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


### $pop modifier ###


class WhenPoppingFromArrayField(object):

    def should_pass_validation(self):
        validate_update_modifier(
            {'$pop': {'field': 1}},
            {'field': [int]})


### $pull modifier ###


class WhenPullingFromArrayField(object):

    def should_pass_validation(self):
        validate_update_modifier(
            {'$pull': {'field': 4}},
            {'field': [int]})


### $pull modifier ###


class WhenPullAllingFromArrayField(object):

    def should_pass_validation(self):
        validate_update_modifier(
            {'$pullAll': {'field': [4, 5]}},
            {'field': [int]})


### $bit modifier ###


class WhenBitModifyingIntField(object):

    def should_pass_validation(self):
        validate_update_modifier(
            {'$bit': {'field': {'and': 5}}},
            {'field': int})


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
