from dingus import Dingus, DingusTestCase
from nose.tools import assert_raises

from scalymongo.connection import DocumentProxy, Connection
import scalymongo.connection as mod


class DescribeConnectionClass(object):

    def should_extend_pymongo_connection(self):
        assert issubclass(Connection, mod.MongoClient)


class BaseConnectionTest(DingusTestCase(Connection)):

    def setup(self):
        super(BaseConnectionTest, self).setup()
        # Resetting this back to the old __init__ seems to break
        # DescribeConnectionClass.
        Connection.__init__ = Dingus(return_value=None)
        Connection.__getitem__ = Dingus('__getitem__')
        self.connection = Connection()


class DescribeConnectDocument(BaseConnectionTest):

    def setup(self):
        BaseConnectionTest.setup(self)
        class MyDoc(object):
            __database__ = Dingus()
            __collection__ = Dingus()
        self.document = MyDoc

        self.returned = self.connection.connect_document(self.document)

    def should_return_subclass_of_original(self):
        assert issubclass(self.returned, self.document)

    def should_set_connection_on_returned(self):
        assert self.returned.connection is self.connection

    def should_set_database_on_returned(self):
        assert self.returned.database == self.connection[
            self.document.__database__]

    def should_set_collection_on_returned(self):
        assert self.returned.collection == self.connection[
            self.document.__database__][self.document.__collection__]


class DescribeModelsGetter(BaseConnectionTest):

    def setup(self):
        BaseConnectionTest.setup(self)

        self.returned = self.connection.models

    def should_create_document_proxy(self):
        assert mod.DocumentProxy.calls(
            '()', self.connection, mod.get_concrete_classes())

    def should_return_document_proxy(self):
        assert mod.DocumentProxy.calls('()').once()
        assert self.returned == mod.DocumentProxy()


class DescribeDocumentProxyInit(object):

    def setup(self):
        self.connection = Dingus('connection')
        self.registered = [
            Dingus(__name__='0'), Dingus(__name__='1'), Dingus(__name__='2')]

        self.returned = DocumentProxy(self.connection, self.registered)

    def should_save_connection(self):
        assert self.returned.connection == self.connection

    def should_map_concrete_names_to_classes(self):
        assert self.returned.registered == {
            '0': self.registered[0],
            '1': self.registered[1],
            '2': self.registered[2],
        }


class WhenDocumentProxyInitWithDuplicateClassNames(
    DingusTestCase(DocumentProxy)):

    def setup(self):
        super(WhenDocumentProxyInitWithDuplicateClassNames, self).setup()
        self.connection = Dingus('connection')
        self.registered = [Dingus(__name__='0'), Dingus(__name__='0')]

        self.returned = DocumentProxy(self.connection, self.registered)

    def should_warn(self):
        assert mod.warnings.calls(
            'warn',
            "Multiple models have been found with the name '0'."
            " The result of connection.models['0'] will be undefined.")


class DescribeDocumentProxy(object):

    def setup(self):
        self.connection = Dingus('connection')
        self.registered = Dingus('registered')
        self.document_proxy = DocumentProxy(self.connection, self.registered)


class WhenGettingUnregisteredItem(DescribeDocumentProxy):

    def should_raise_key_error(self):
        assert_raises(KeyError, self.document_proxy.__getitem__, 'Document')


class WhenGettingUnregisteredViaAttr(DescribeDocumentProxy):

    def should_raise_key_error(self):
        assert_raises(AttributeError, getattr, self.document_proxy, 'Document')


class BaseDocumentRegistered(DescribeDocumentProxy):

    def setup(self):
        DescribeDocumentProxy.setup(self)
        self.cls = Dingus('Document')
        self.document_proxy.registered['Document'] = self.cls

    def should_connect_document(self):
        assert self.connection.calls('connect_document', self.cls)

    def should_return_connected_document(self):
        assert self.connection.calls('connect_document').once()
        assert self.returned == self.connection.connect_document()


class WhenGettingItem(BaseDocumentRegistered):

    def setup(self):
        BaseDocumentRegistered.setup(self)
        self.returned = self.document_proxy['Document']


class WhenGettingAttr(BaseDocumentRegistered):

    def setup(self):
        BaseDocumentRegistered.setup(self)
        self.returned = self.document_proxy.Document


class WhenIterating(DescribeDocumentProxy):

    def setup(self):
        DescribeDocumentProxy.setup(self)
        self.registered  = {'x': Dingus(), 'y': Dingus()}
        self.document_proxy.registered = self.registered
        self.returned = [x for x in self.document_proxy]

    def should_return_connected_documents(self):
        assert self.returned == [
            self.connection.connect_document(),
            self.connection.connect_document(),
        ]

    def should_connect_documents(self):
        assert self.connection.calls('connect_document', self.registered['x'])
        assert self.connection.calls('connect_document', self.registered['y'])
