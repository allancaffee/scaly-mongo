from scalymongo import Connection


class BaseAcceptanceTest(object):

    @classmethod
    def setup_class(cls):
        cls.connection = Connection()
