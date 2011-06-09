from scalymongo import Document
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class Comment(Document):
    structure = {
        'author': basestring,
        'comment': basestring,
        'rank': int,
    }


class Statistics(Document):
    structure = {
        'total_views': int,
        'unique_views': int,
    }


class BlogPost(Document):
    structure = {
        'author': basestring,
        'title': basestring,
        'body': basestring,
        'comments': [Comment],
        'statistics': Statistics,
    }
    __database__ = 'test'
    __collection__ = __name__


class TestEmbeddedDocument(BaseAcceptanceTest):

    @classmethod
    def setup_class(cls):
        BaseAcceptanceTest.setup_class()
        cls.doc = cls.connection.models.BlogPost()
        cls.doc.author = 'Alice'
        cls.doc.title = 'Some title'
        cls.doc.body = 'Body text'
        cls.comment = Comment(author='Bob', comment='A comment', rank=0)
        cls.doc.comments = [cls.comment]
        cls.doc.statistics = Statistics(total_views=10, unique_views=7)
        cls.doc.save()

        cls.loaded_doc = cls.connection.models.BlogPost.find_one(cls.doc._id)

    def should_return_comments_as_comment_objects(self):
        assert isinstance(self.loaded_doc.comments[0], Comment)

    def should_return_statistics_item_as_statistics_object(self):
        assert isinstance(self.loaded_doc['statistics'], Statistics)

    def should_return_statistics_attr_as_statistics_object(self):
        assert isinstance(self.loaded_doc.statistics, Statistics)
