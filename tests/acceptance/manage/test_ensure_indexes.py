import os
import subprocess

from tests.acceptance.base_acceptance_test import BaseAcceptanceTest
import tests.acceptance.manage.ensure_indexes_documents


def run_ensure_indexes():
    """Run ensure_indexes.py with the example documents.
    """
    os.environ['PYTHONPATH'] = os.getcwd()
    process_args = [
        'python',
        'scalymongo/manage/ensure_indexes.py',
        'tests.acceptance.manage.ensure_indexes_documents',
        'localhost:27017',
    ]
    return subprocess.check_call(process_args)


class TestEnsureIndex(BaseAcceptanceTest):

    @classmethod
    def setup_class(cls):
        BaseAcceptanceTest.setup_class()
        cls.ConnectedEnsureIndexExampleA \
             = cls.connection.models.EnsureIndexExampleA
        cls.ConnectedEnsureIndexExampleA.collection.drop()

        run_ensure_indexes()

        cls.indexes \
            = cls.ConnectedEnsureIndexExampleA.collection.index_information()

    def should_create_index_on_a_b(self):
        index = self.indexes['a_1_b_1']
        assert index['key'] == [('a', 1), ('b', 1)]
        assert index['unique'] is True
