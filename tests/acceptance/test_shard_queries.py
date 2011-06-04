from nose.tools import assert_raises

from scalymongo import Document
from scalymongo.errors import GlobalQueryException
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class ShardQueryExample(Document):
    structure = {
        'name': basestring,
        'age': int,
        'other': basestring,
    }
    indexes = [{
        'fields': ['name', 'age'],
        'shard_key': True,
    }]

    __database__ = 'test'
    __collection__ = __name__


class BaseShardQueryTest(BaseAcceptanceTest):

    @classmethod
    def setup_class(cls):
        BaseAcceptanceTest.setup_class()
        cls.connection.models.ShardQueryExample.collection.drop()

        cls.docs = [
            {'name': 'Alice', 'age': 32},
            {'name': 'Bob', 'age': 32},
            {'name': 'Carl', 'age': 41},
        ]
        cls.docs = [cls.connection.models.ShardQueryExample(doc)
                    for doc in cls.docs]
        for doc in cls.docs:
            doc.save()


class WhenFindingByAge(BaseShardQueryTest):

    def should_raise_global_query_exception(self):
        assert_raises(
            GlobalQueryException,
            self.connection.models.ShardQueryExample.find,
            {'age':32})


class WhenNoDocumentsMatch(BaseShardQueryTest):

    @classmethod
    def setup_class(cls):
        BaseShardQueryTest.setup_class()

        cls.returned = cls.connection.models.ShardQueryExample\
                       .find_one({'name': 'John', 'age': 50})

    def should_return_none(self):
        assert self.returned is None
