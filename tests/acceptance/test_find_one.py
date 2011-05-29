from scalymongo import Document, ObjectId
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class FindOneExample(Document):
    structure = {
        'name': basestring,
        'age': int,
    }

    __database__ = 'test'
    __collection__ = __file__


class BaseFindOneTest(BaseAcceptanceTest):

    @classmethod
    def setup_class(cls):
        BaseAcceptanceTest.setup_class()
        cls.connection.models.FindOneExample.collection.drop()
        cls.doc = cls.connection.models.FindOneExample()
        cls.doc['name'] = 'Alice'
        cls.doc['age'] = 32
        cls.doc.save()


class WhenFindingOneById(BaseFindOneTest):

    @classmethod
    def setup_class(cls):
        BaseFindOneTest.setup_class()

        cls.returned = cls.connection.models.FindOneExample.find_one(
            {'_id': cls.doc['_id']})

    def should_find_identical_document(self):
        assert self.returned == self.doc

    def should_return_user_instance(self):
        assert isinstance(self.returned, FindOneExample)


class WhenFindingOneWithoutArgs(BaseFindOneTest):

    @classmethod
    def setup_class(cls):
        BaseFindOneTest.setup_class()

        cls.returned = cls.connection.models.FindOneExample.find_one()

    def should_find_identical_document(self):
        assert self.returned == self.doc

    def should_return_user_instance(self):
        assert isinstance(self.returned, FindOneExample)


class WhenNoDocumentsMatch(BaseFindOneTest):

    @classmethod
    def setup_class(cls):
        BaseFindOneTest.setup_class()

        cls.returned = cls.connection.models.FindOneExample.find_one(
            {'name': 'Bob'})

    def should_return_none(self):
        assert self.returned is None
