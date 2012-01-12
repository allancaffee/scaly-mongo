from nose.tools import assert_raises

from scalymongo import Document, OR, IS
from scalymongo.errors import ValidationError
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest
from tests.helpers import assert_raises_with_message


class DocumentWithListOfStrings(Document):
    structure = {
        'field': [basestring],
    }

    __database__ = 'test'
    __collection__ = __name__ + '_0'


def when_validating_empty_document_should_pass():
    DocumentWithListOfStrings({}).validate()

def when_validating_document_with_empty_list_should_pass():
    DocumentWithListOfStrings({'field': []}).validate()

def when_validating_document_with_list_of_strings():
    DocumentWithListOfStrings({'field': ['str', u'unicode']}).validate()

def when_validating_document_with_list_of_numbers():
    assert_raises_with_message(
        ValidationError,
        "Position 'field.0' was declared to be <type 'basestring'>, but encountered value 1",
        DocumentWithListOfStrings({'field': [1]}).validate)

def when_validating_document_with_extra_fields_should_raise_error():
    doc = DocumentWithListOfStrings({'unknown': 1})
    assert_raises_with_message(
        ValidationError,
        "Encountered field(s) not present in structure: 'unknown'",
        doc.validate)


class DocumentWithEmbeddedDictOfStringToInt(Document):
    structure = {
        'field': {basestring: int},
    }

    __database__ = 'test'
    __collection__ = __name__ + '_1'


def when_validating_proper_embedded_dict_should_pass():
    doc = DocumentWithEmbeddedDictOfStringToInt({
        'field': {'foo': 1, u'bar': 2}})
    doc.validate()

def when_validating_document_with_string_mapped_to_float_should_fail_validation():
    doc = DocumentWithEmbeddedDictOfStringToInt({
        'field': {'foo': 1, u'bar': 2.3}})
    assert_raises_with_message(
        ValidationError,
        "Position 'field.bar' was declared to be <type 'int'>, but encountered value 2.2999999999999998",
        doc.validate)


class DocumentWithMultiplePotentialTypes(Document):
    structure = {
        'field': OR(basestring, int),
    }

    __database__ = 'test'
    __collection__ = __name__ + '_2'


def when_validating_with_int_field_should_pass():
    DocumentWithMultiplePotentialTypes({'field': 5}).validate()

def when_validating_with_string_should_pass():
    DocumentWithMultiplePotentialTypes({'field': 'foo'}).validate()

def when_validating_with_list_of_int_should_fail():
    assert_raises_with_message(
        ValidationError,
        "Position 'field' was declared to be <OR <type 'int'>, <type 'basestring'>>, but encountered value [1]",
        DocumentWithMultiplePotentialTypes({'field': [1]}).validate)


class DocumentWithMultiplePotentialValues(Document):
    structure = {
        'field': IS(1, 'foo'),
    }

    __database__ = 'test'
    __collection__ = __name__ + '_3'


def when_validating_with_1_field_should_pass():
    DocumentWithMultiplePotentialValues({'field': 1}).validate()

def when_validating_with_foo_should_pass():
    DocumentWithMultiplePotentialValues({'field': 'foo'}).validate()

def when_validating_with_2_should_fail():
    assert_raises_with_message(
        ValidationError,
        "Position 'field' was declared to be <IS 1, 'foo'>, but encountered value 2",
        DocumentWithMultiplePotentialValues({'field': 2}).validate)
