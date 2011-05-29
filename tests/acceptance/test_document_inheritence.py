import datetime

from scalymongo import Document


class User(Document):

    abstract = True
    structure = {
        'username': unicode,
        'password': str,
        'join_date': datetime.datetime,
    }

    indexes = [
        {'fields': 'username', 'unique': True},
    ]

    required_fields = ['username', 'password', 'join_date']


class Customer(User):

    structure = {
        'paid': {
            'dollars': int,
            'cents': int,
        }
    }

    indexes = [
        {'fields': ['paid.dollars', 'paid.cents']},
    ]


class TestDocumentInheritence(object):

    def should_merge_structure(self):
        assert Customer.structure == {
            'username': unicode,
            'password': str,
            'join_date': datetime.datetime,
            'paid': {
                'dollars': int,
                'cents': int,
            },
        }

    def should_merge_indexes(self):
        assert Customer.indexes == [
            {'fields': ['paid.dollars', 'paid.cents']},
            {'fields': 'username', 'unique': True},
        ]
