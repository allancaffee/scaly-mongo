from nose.tools import assert_raises

from scalymongo.errors import UnsafeBehaviorError
from scalymongo import Document, ObjectId
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class User(Document):
    structure = {
        'name': basestring,
        'age': int,
    }

    __database__ = 'test'
    __collection__ = 'users'
    write_concern_override = {'w': 0}


class BaseSaveTest(BaseAcceptanceTest):

    @classmethod
    def setup_class(cls):
        BaseAcceptanceTest.setup_class()
        cls.doc = cls.connection.models.User()
        cls.doc['name'] = 'Alice'
        cls.doc['age'] = 32

    def should_have_non_default_write_concern(self):
        assert self.doc.collection.write_concern == {'w': 0}


class TestSave(BaseSaveTest):

    @classmethod
    def setup_class(cls):
        BaseSaveTest.setup_class()
        cls.doc.save()

    def should_have_id_field(self):
        assert '_id' in self.doc

    def should_have_object_id_in_id_field(self):
        assert isinstance(self.doc['_id'], ObjectId)


class TestDoubleSave(BaseSaveTest):

    @classmethod
    def setup_class(cls):
        BaseSaveTest.setup_class()
        cls.doc.save()

    def should_not_allow_resave(self):
        assert_raises(UnsafeBehaviorError, self.doc.save)
