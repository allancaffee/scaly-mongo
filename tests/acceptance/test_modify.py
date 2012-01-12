import datetime

from nose.tools import assert_raises

from scalymongo import Document
from scalymongo.errors import ModifyFailedError
from tests.acceptance.base_acceptance_test import BaseAcceptanceTest


class BlogPostModifyExample(Document):

    __collection__ = __name__
    __database__ = 'test'
    structure = {
        'author': basestring,
        'title': basestring,
        'body': basestring,
        'views': int,
        'comments': [{
            'author': basestring,
            'comment': basestring,
            'rank': int,
        }],
    }
    default_values = {
        'views': 0,
    }


EXAMPLE_POST = {
    'author': 'Alice',
    'title': 'Writing Scalable Services with Python and MongoDB',
    'body': 'Use ScalyMongo!',
}


class BlogPostTestCase(BaseAcceptanceTest):

    def setup(self):
        self.doc = self.connection.models.BlogPostModifyExample(EXAMPLE_POST)
        self.doc.save()

    def teardown(self):
        self.connection.models.BlogPostModifyExample.collection.drop()

    def is_document_up_to_date(self):
        """True if and only if ``self.doc`` reflects what's in the database."""
        fresh_copy = self.connection.models.BlogPostModifyExample.find_one(
            self.doc.shard_key)
        return self.doc == fresh_copy

    def when_no_precondition_given_should_increment(self):
        self.doc.modify({'$inc': {'views': 1}})
        assert self.doc.views == 1

        self.doc.modify({'$inc': {'views': 5}})
        assert self.doc.views == 6

        assert self.is_document_up_to_date()

    def when_precondition_fails_should_raise_ModifyFailedError(self):
        assert_raises(
            ModifyFailedError,
            self.doc.modify,
            {'$set': {'author': 'Bob'}},
            {'author': 'Not Alice'},
        )

        # The doc should not have been altered.
        assert self.doc.author == 'Alice'
        assert self.is_document_up_to_date()

    def when_precondition_passes_should_update_field(self):
        self.doc.modify(
            {'$set': {'views': 15}},
            {'author': 'Alice'},
        )

        assert self.is_document_up_to_date()

    def when_pushing_valid_comment_should_pass_validation(self):
        comment = {
            'author': 'Bob',
            'comment': 'Mongo is great!',
            'rank': 0,
        }
        self.doc.modify({'$push': {'comments': comment}})

        assert self.doc.comments == [comment]
