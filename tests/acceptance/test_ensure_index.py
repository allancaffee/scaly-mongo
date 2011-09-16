from tests.acceptance.base_acceptance_test import BaseAcceptanceTest
from scalymongo import Document


class IndexTestDocument(Document):
    structure = {
        'number': int,
        'name': unicode,
        'descending': int,
        'ascending': int,
    }
    indexes = [
        {'fields': 'number'},
        {'fields': 'name', 'unique': True},
        {'fields': [('descending', -1), ('ascending', 1)]}
    ]
    __database__ = 'test'
    __collection__ = 'IndexTestDocument'


class TestEnsureIndex(BaseAcceptanceTest):

    @classmethod
    def setup_class(cls):
        BaseAcceptanceTest.setup_class()
        cls.connected_document = cls.connection.models.IndexTestDocument
        cls.connected_document.collection.drop()

        cls.connected_document.ensure_indexes()

        cls.indexes = cls.connected_document.collection.index_information()

    def should_create_index_on_number(self):
        index = self.indexes['number_1']
        assert index['key'] == [('number', 1)]
        assert index.get('unique', False) is False

    def should_create_unique_index_on_name(self):
        index = self.indexes['name_1']
        assert index['key'] == [('name', 1)]
        assert index['unique'] is True

    def should_create_descending_ascending_index(self):
        index = self.indexes['descending_-1_ascending_1']
        assert index['key'] == [('descending', -1), ('ascending', 1)]
        assert index.get('unique', False) is False
