from nose.tools import assert_raises

from scalymongo import Document
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
        "Position 'field.bar' was declared to be <type 'int'>, but encountered value 2.3",
        doc.validate)
