# -*- coding: utf-8 -*-
from dingus import Dingus, DingusTestCase, DontCare
from nose.tools import assert_raises

from scalymongo.schema import *
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


class DescribeValidateStructure(
    DingusTestCase(validate_structure, ['ValidationError'])):

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
