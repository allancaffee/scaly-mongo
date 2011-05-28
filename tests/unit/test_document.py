from dingus import DingusTestCase, Dingus
from nose.tools import assert_raises

from scalymongo.document import *
import scalymongo.document as mod


class BaseDocumentMetaclassNew(
    DingusTestCase(DocumentMetaclass)):

    def setup(self):
        super(BaseDocumentMetaclassNew, self).setup()
        self.name = Dingus()
        self.bases = Dingus()
        self.attrs = {}
        mod.SchemaMetaclass.__new__ = Dingus()

    def should_create_new_document_class(self):
        assert mod.SchemaMetaclass.__new__.calls(
            '()', DocumentMetaclass, self.name, self.bases, self.attrs)

    def should_return_new_class(self):
        assert self.returned == mod.SchemaMetaclass.__new__()


class WhenDocumentClassIsAbstract(BaseDocumentMetaclassNew):

    def setup(self):
        BaseDocumentMetaclassNew.setup(self)
        self.attrs['abstract'] = True

        self.returned = DocumentMetaclass.__new__(
            DocumentMetaclass, self.name,
            self.bases, self.attrs)

    def should_not_add_to_concrete_classes(self):
        assert self.returned not in DocumentMetaclass.concrete_classes


class WhenDocumentClassIsNotAbstract(BaseDocumentMetaclassNew):

    def setup(self):
        BaseDocumentMetaclassNew.setup(self)

        self.returned = DocumentMetaclass.__new__(
            DocumentMetaclass, self.name,
            self.bases, self.attrs)

    def should_add_to_concrete_classes(self):
        assert self.returned in DocumentMetaclass.concrete_classes


class DescribeGetConcreteClasses(DingusTestCase(get_concrete_classes)):

    def setup(self):
        super(DescribeGetConcreteClasses, self).setup()

        self.returned = get_concrete_classes()

    def should_return_concrete_classes(self):
        assert self.returned == mod.DocumentMetaclass.concrete_classes


class DescribeDocumentClass(object):

    def should_have_document_metaclass(self):
        assert Document.__metaclass__ is DocumentMetaclass

    def should_be_abstract(self):
        assert Document.abstract is True


class BaseDocumentTest(DingusTestCase(Document, ['UnsafeBehaviorError'])):

    def setup(self):
        super(BaseDocumentTest, self).setup()
        self.doc = Document()
        self.doc.connection = Dingus('connection')


class BaseSaveTest(BaseDocumentTest):

    def setup(self):
        BaseDocumentTest.setup(self)
        self.doc.__collection__ = Dingus('__collection__')
        self.doc.__database__ = Dingus('__database__')
        self.doc.validate = Dingus('validate')


class WhenDocumentHasAnId(BaseSaveTest):

    def setup(self):
        BaseSaveTest.setup(self)
        self.doc['_id'] = Dingus('_id')

    def should_raise_exception_without_saving(self):
        assert_raises(UnsafeBehaviorError, self.doc.save)
        assert not self.doc.collection.calls('insert')


class WhenDocumentHasNoId(BaseSaveTest):

    def setup(self):
        BaseSaveTest.setup(self)

        self.doc.save()

    def should_validate_document(self):
        assert self.doc.validate.calls('()')

    def should_insert_document_into_collection(self):
        assert self.doc.collection.calls('insert', self.doc)


class DescribeCollectionGetter(BaseDocumentTest):

    def setup(self):
        BaseDocumentTest.setup(self)
        self.doc.__collection__ = Dingus('__collection__')
        self.doc.__database__ = Dingus('__database__')

        self.returned = self.doc.collection

    def should_return_collection_from_database(self):
        assert self.returned == self.doc.database[self.doc.__collection__]


class DescribeDatabaseGetter(BaseDocumentTest):

    def setup(self):
        BaseDocumentTest.setup(self)
        self.doc.__database__ = Dingus('__database__')

        self.returned = self.doc.database

    def should_return_database_from_connection(self):
        assert self.returned == self.doc.connection[self.doc.__database__]
