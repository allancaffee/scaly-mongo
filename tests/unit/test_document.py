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


class WhenDocumentClassHasConnection(BaseDocumentMetaclassNew):

    def setup(self):
        BaseDocumentMetaclassNew.setup(self)
        self.attrs['connection'] = Dingus('connection')

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
        self.doc.collection = Dingus('collection')
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


class DescribeEnsureIndexes(object):

    def setup(self):
        self.index0 = {'fields': Dingus()}
        self.index1 = {'fields': Dingus()}
        class MyDoc(Document):
            collection = Dingus()
            indexes = [
                self.index0,
                self.index1,
            ]
        self.MyDoc = MyDoc
        MyDoc.ensure_indexes()

    def should_ensure_indexes(self):
        assert self.MyDoc.collection.calls(
            'ensure_index', self.index0['fields'], unique=False)
        assert self.MyDoc.collection.calls(
            'ensure_index', self.index1['fields'], unique=False)


class WhenUniqueIndex(object):

    def setup(self):
        class MyDoc(Document):
            collection = Dingus()
            indexes = [
                {'fields': Dingus(),
                 'unique': True}
            ]
        self.MyDoc = MyDoc
        MyDoc.ensure_indexes()

    def should_ensure_indexes(self):
        assert self.MyDoc.collection.calls(
            'ensure_index',
            self.MyDoc.indexes[0]['fields'],
            unique=True)