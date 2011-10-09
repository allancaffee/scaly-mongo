from scalymongo import Document


class EnsureIndexExampleA(Document):

    structure = {
        'a': int,
        'b': int,
        'c': str,
    }

    indexes = [{
        'fields': [('a', 1), ('b', 1)],
        'unique': True,
        'shard_key': True,
    }]
    __database__ = 'ensure_index_documents'
    __collection__ = 'ensure_index_example_a'
