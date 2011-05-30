from scalymongo import Document
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class FindAndModifyExample(Document):
    structure = {
        'name': basestring,
        'age': int,
    }

    __database__ = 'test'
    __collection__ = __file__


class BaseFindAndModifyTest(BaseAcceptanceTest):

    @classmethod
    def setup_class(cls):
        BaseAcceptanceTest.setup_class()
        cls.connection.models.FindAndModifyExample.collection.drop()

        cls.docs = [
            {'name': 'Alice', 'age': 32},
            {'name': 'Bob', 'age': 32},
            {'name': 'Carl', 'age': 41},
        ]
        cls.docs = [cls.connection.models.FindAndModifyExample(doc)
                    for doc in cls.docs]
        for doc in cls.docs:
            doc.save()


class WhenFindAndModifyingByAge(BaseFindAndModifyTest):

    @classmethod
    def setup_class(cls):
        BaseFindAndModifyTest.setup_class()

        cls.returned = cls.connection.models.FindAndModifyExample\
                       .find_and_modify({'age': 41}, {'$inc': {'age': 1}})

    def should_find_carl(self):
        assert self.returned == self.docs[2]

    def should_have_incremented_carls_age_in_db(self):
        assert self.connection.models.FindAndModifyExample.find_one(
            {'name': 'Carl', 'age': 42, '_id': self.docs[2]['_id']})


class WhenNoDocumentsMatch(BaseFindAndModifyTest):

    @classmethod
    def setup_class(cls):
        BaseFindAndModifyTest.setup_class()

        cls.returned = cls.connection.models.FindAndModifyExample\
                       .find_and_modify({'name': 'John'}, {'$inc': {'age': 1}})

    def should_return_none(self):
        assert self.returned is None
