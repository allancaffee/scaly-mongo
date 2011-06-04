from nose.tools import assert_raises

from scalymongo import Document
from scalymongo.errors import GlobalQueryException
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class BaseSchemaMergeTest(BaseAcceptanceTest):

    @classmethod
    def setup_class(cls):
        BaseAcceptanceTest.setup_class()

        cls.shard_index = {
            'fields': ['name', 'age'],
            'shard_key': True,
        }

        class SchemaMergingExample(Document):
            structure = {
                'name': basestring,
                'age': int,
                'other': basestring,
            }
            indexes = [cls.shard_index]

            __database__ = 'test'
            __collection__ = __name__

        cls.SchemaMergingExample = SchemaMergingExample
        cls.connected_model = cls.connection.models.SchemaMergingExample

    def should_have_shard_index(self):
        assert self.SchemaMergingExample.shard_index == self.shard_index

    def should_have_shard_index_on_connected_model(self):
        assert self.connected_model.shard_index == self.shard_index

    def should_have_indexes_on_connected_model(self):
        assert self.connected_model.indexes == self.SchemaMergingExample.indexes
