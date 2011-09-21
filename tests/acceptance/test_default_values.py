from scalymongo import Document
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class Theme(Document):

    __database__ = 'test'
    __collection__ = __name__

    structure = {
        'name': unicode,
        'layout': [unicode],
        'dictionary': dict,
    }
    required_fields = set([
        'dictionary',
        'layout',
        'name',
    ])
    default_values = {
        'layout': list,
        'dictionary': dict,
    }


class WhenDocumentHasDefaultsAndEmbeddedDict(BaseAcceptanceTest):
    """
    This test case was written to address Issue #4
    (https://github.com/allancaffee/scaly-mongo/issues/4).
    """

    source_doc = {
        'dictionary': {'foo': '1', 'bar': '2'},
        'layout': [u'foo', u'bar'],
        'name': u'Testing 1 2 3',
    }

    @classmethod
    def setup_class(cls):
        BaseAcceptanceTest.setup_class()

        cls.theme = cls.connection.models.Theme(cls.source_doc)
        cls.theme.save()
        cls.loaded_theme = cls.theme.find_one(cls.theme._id)

    def should_be_identical_to_original_document(self):
        assert self.loaded_theme == self.theme

    def should_be_identical_to_source_doc_plus_id(self):
        source_with_id = dict(self.source_doc, _id=self.theme._id)
        assert self.loaded_theme == source_with_id
