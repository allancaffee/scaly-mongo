from scalymongo import Document
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class FindExample(Document):
    structure = {
        'name': basestring,
        'age': int,
    }

    indexes = [{
        'fields': [('name', 1)],
    }]

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
            {'name': 'Donna', 'age': 35},
        ]
        cls.docs = [cls.connection.models.FindExample(doc)
                    for doc in cls.docs]
        for doc in cls.docs:
            doc.save()

        cls.connection.models.FindExample.ensure_indexes()

    @classmethod
    def teardown_class(cls):
        super(BaseFindTest, cls).teardown_class()
        cls.connection.models.FindExample.collection.drop()


class PropertyReturnsScalyMongoDocuments(object):

    def should_return_only_find_example_instances(self):
        for returned_doc in self.returned_docs:
            assert isinstance(returned_doc, FindExample)


class WhenFindingByAge(BaseFindTest):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find({'age': 32})
        cls.returned_docs = list(cls.returned)

    def should_find_alice_and_bob(self):
        assert self.returned_docs == self.docs[:2]

    def should_return_2_results(self):
        assert self.returned.count() == 2


class WhenFindingWithoutArgs(BaseFindTest, PropertyReturnsScalyMongoDocuments):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find()
        cls.returned_docs = list(cls.returned)

    def should_find_all(self):
        assert self.returned_docs == self.docs


class WhenFindingWithoutArgsOnRewoundCursor(BaseFindTest):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find()
        cls.first_returned_docs = list(cls.returned)
        cls.returned = cls.returned.rewind()
        cls.second_returned_docs = list(cls.returned)

    def should_find_all(self):
        assert self.first_returned_docs == self.docs
        assert self.second_returned_docs == self.docs

    def should_return_find_example_instances(self):
        for doc in self.first_returned_docs:
            assert isinstance(doc, FindExample)
        for doc in self.second_returned_docs:
            assert isinstance(doc, FindExample)


class WhenFindingWithoutArgsOnClonedCursor(BaseFindTest):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find()
        cls.first_returned_docs = list(cls.returned)
        cls.returned = cls.returned.clone()
        cls.second_returned_docs = list(cls.returned)

    def should_find_all(self):
        assert self.first_returned_docs == self.docs
        assert self.second_returned_docs == self.docs

    def should_return_find_example_instances(self):
        for doc in self.first_returned_docs:
            assert isinstance(doc, FindExample)
        for doc in self.second_returned_docs:
            assert isinstance(doc, FindExample)


class WhenNoDocumentsMatch(BaseFindTest):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find(
            {'name': 'John'})
        cls.returned_docs = list(cls.returned)

    def should_return_0_results(self):
        assert self.returned.count() == 0


class WhenFindingWithSkip(BaseFindTest, PropertyReturnsScalyMongoDocuments):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find().skip(1)
        cls.returned_docs = list(cls.returned)

    def should_return_Bob_and_Carl(self):
        assert self.returned_docs == self.docs[1:]


class WhenFindingWithLimit(BaseFindTest, PropertyReturnsScalyMongoDocuments):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find().limit(1)
        cls.returned_docs = list(cls.returned)

    def should_return_only_first(self):
        assert self.returned_docs == [self.docs[0]]


class WhenSortingByNameInverted(BaseFindTest, PropertyReturnsScalyMongoDocuments):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find().sort(
            [('name', -1)])
        cls.returned_docs = list(cls.returned)

    def should_return_4_results(self):
        assert self.returned.count() == 4

    def should_return_Donna_Carl_Bob_and_Alice(self):
        assert self.returned_docs[0] == self.docs[-1]
        assert self.returned_docs[1] == self.docs[-2]
        assert self.returned_docs[2] == self.docs[-3]
        assert self.returned_docs[3] == self.docs[-4]


class WhenFilteringWithAWhereClause(BaseFindTest, PropertyReturnsScalyMongoDocuments):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find().where(
            'this.age>35')
        cls.returned_docs = list(cls.returned)

    def should_return_1_result(self):
        assert self.returned.count() == 1

    def should_return_Carl(self):
        assert self.returned_docs == [self.docs[2]]


class WhenGettingASlice(BaseFindTest):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find()[1:2]
        cls.returned_docs = list(cls.returned)

    def should_return_Bob_and_Carl(self):
        assert self.returned_docs == self.docs[1:2]

    def should_return_1_result(self):
        assert self.returned.count(True) == 1


class WhenFindingAge32WithMaxScanOf1(
        BaseFindTest, PropertyReturnsScalyMongoDocuments):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find(
            {'age': 32}).max_scan(1)
        cls.returned_docs = list(cls.returned)

    def should_return_only_Alice(self):
        assert self.returned_docs == [self.docs[0]]


class WhenFindingAllWithHint(BaseFindTest, PropertyReturnsScalyMongoDocuments):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find().hint(
            [('name', 1)])
        cls.returned_docs = list(cls.returned)

    def should_find_all(self):
        assert self.returned_docs == self.docs


class WhenFindingAllWithBatchSize(BaseFindTest, PropertyReturnsScalyMongoDocuments):

    @classmethod
    def setup_class(cls):
        BaseFindTest.setup_class()

        cls.returned = cls.connection.models.FindExample.find().batch_size(5)
        cls.returned_docs = list(cls.returned)

    def should_find_all(self):
        assert self.returned_docs == self.docs
