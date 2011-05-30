from scalymongo import Document
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class FindExample(Document):
    structure = {
        'name': basestring,
        'age': int,
    }

    __database__ = 'test'
    __collection__ = __file__


class BaseFindTest(BaseAcceptanceTest):

    @classmethod
    def setup_class(cls):
        BaseAcceptanceTest.setup_class()
        cls.connection.models.FindExample.collection.drop()

        cls.docs = [
            {'name': 'Alice', 'age': 32},
            {'name': 'Bob', 'age': 32},
            {'name': 'Carl', 'age': 41},
        ]
        cls.docs = [cls.connection.models.FindExample(doc)
                    for doc in cls.docs]
        for doc in cls.docs:
            doc.save()


class WhenFindingByAge(BaseFindTest):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find({'age': 32})
        cls.returned_docs = [doc for doc in cls.returned]

    def should_find_alice_and_bob(self):
        assert self.returned_docs == self.docs[:2]

    def should_return_2_results(self):
        assert self.returned.count() == 2

    def should_return_find_example_instances(self):
        assert isinstance(self.returned_docs[0], FindExample)
        assert isinstance(self.returned_docs[1], FindExample)


class WhenFindingWithoutArgs(BaseFindTest):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find()
        cls.returned_docs = [doc for doc in cls.returned]

    def should_find_all(self):
        assert self.returned_docs == self.docs

    def should_return_find_example_instances(self):
        assert isinstance(self.returned_docs[0], FindExample)
        assert isinstance(self.returned_docs[1], FindExample)
        assert isinstance(self.returned_docs[2], FindExample)


class WhenNoDocumentsMatch(BaseFindTest):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find(
            {'name': 'John'})

    def should_return_0_results(self):
        assert self.returned.count() == 0
