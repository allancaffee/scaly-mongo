from scalymongo import Connection


class BaseAcceptanceTest(object):

    @classmethod
    def setup_class(cls):
        cls.connection = Connection()

    @classmethod
    def teardown_class(cls):
        cls.connection.disconnect()
