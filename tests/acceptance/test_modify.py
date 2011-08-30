import datetime

from nose.tools import assert_raises

from scalymongo import Document
from scalymongo.errors import ModifyFailedError
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class ModifyableDocument(Document):

    __collection__ = __name__
    __database__ = 'test'
    structure = {
        'field': basestring,
    }


class WhenModifyingDocumentAndPreconditionFails(BaseAcceptanceTest):

    def should_raise_ModifyFailedError(self):
        doc = self.connection.models.ModifyableDocument({'field': 'foo'})
        doc.save()
        assert_raises(
            ModifyFailedError,
            doc.modify,
            {'field': 'not the correct value'},
            {'$set': {'field': 'new value'}},
        )
