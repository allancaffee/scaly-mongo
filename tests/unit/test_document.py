from dingus import DingusTestCase, Dingus, exception_raiser
from nose.tools import assert_raises

from scalymongo.document import *
from scalymongo.errors import GlobalQueryException
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


class WhenReloadingDocumentWithoutShardKey(object):

    def setup(self):
        class MyDoc(Document):
            structure = {
                'foo': int,
                'bar': basestring,
                'biz': float,
            }
        self.MyDoc = MyDoc
        self.doc = self.MyDoc({'_id': Dingus('_id'),
                               'foo': 1, 'bar': 'moo', 'biz': 3.3})
        self.doc.find_one = Dingus(
            'find_one', return_value={'foo': 1, 'bar': 'moo', 'biz': 5.5})

        self.doc.reload()

    def should_set_biz_to_5_point_5(self):
        assert self.doc['biz'] == 5.5

    def should_find_one_using_just_id(self):
        assert self.doc.find_one.calls(
            '()', {'_id': self.doc['_id']})


class WhenReloadingDocumentWithShardKey(object):

    def setup(self):
        class MyDoc(Document):
            structure = {
                'foo': int,
                'bar': basestring,
                'biz': float,
            }
            indexes = [
                {'fields': ['foo', 'bar'],
                 'shard_key': True}
            ]
        self.MyDoc = MyDoc
        self.doc = self.MyDoc({'_id': Dingus('_id'),
                               'foo': 1, 'bar': 'moo', 'biz': 3.3})
        self.doc.find_one = Dingus(
            'find_one', return_value={'foo': 1, 'bar': 'moo', 'biz': 5.5})

        self.doc.reload()

    def should_find_one_using_shard_key(self):
        assert self.doc.find_one.calls(
            '()', {'_id': self.doc['_id'], 'foo': 1, 'bar': 'moo'})


## Document.modify ##

class BaseModify(object):

    def setup(self):
        class MyDoc(Document):
            structure = {
                'foo': int,
                'bar': basestring,
                'biz': float,
            }
            indexes = [
                {'fields': ['foo', 'bar'],
                 'shard_key': True}
            ]
            find_and_modify = Dingus('find_and_modify')

        self.MyDoc = MyDoc
        self.my_doc = MyDoc({
            '_id': Dingus('_id'),
            'foo': Dingus('foo'),
            'bar': Dingus('bar'),
            'biz': Dingus('biz'),
        })
        self.original_my_doc = dict(self.my_doc)
        self.update = Dingus('update')
        self.MyDoc.find_and_modify.return_value = {
            '_id': self.my_doc['_id'],
            'bar': Dingus('bar2'),
            'biz': Dingus('biz2'),
            'quizblorg': Dingus('quizblorg'),
            'bandersnatch': Dingus('bandersnatch'),
        }


class PropertyModifyUpdatesLocalCopy(object):

    def should_merge_result_from_find_and_modify(self):
        assert self.my_doc == self.MyDoc.find_and_modify()


class PropertyModifyWithDefaultQuerySpec(object):

    def should_find_and_modify_document(self):
        query = {'_id': self.original_my_doc['_id'],
                 'foo': self.original_my_doc['foo'],
                 'bar': self.original_my_doc['bar']}
        assert self.MyDoc.find_and_modify.calls(
            '()', query, self.update, new=True)


class PropertyModifyWithExplicitQuerySpec(object):

    def should_find_and_modify_document(self):
        query = {'_id': self.original_my_doc['_id'],
                 'foo': self.original_my_doc['foo'],
                 'bar': self.original_my_doc['bar']}
        query.update(self.query)
        assert self.MyDoc.find_and_modify.calls(
            '()', query, self.update, new=True)


class TestModifyWithoutQuerySpec(
    BaseModify,
    PropertyModifyWithDefaultQuerySpec,
    PropertyModifyUpdatesLocalCopy,
    ):

    def setup(self):
        BaseModify.setup(self)
        self.my_doc.modify(self.update)


class TestModifyWithExplicitQuerySpec(
    BaseModify,
    PropertyModifyWithExplicitQuerySpec,
    PropertyModifyUpdatesLocalCopy,
    ):

    def setup(self):
        BaseModify.setup(self)
        self.query = {'blarg': Dingus('blarg')}
        self.my_doc.modify(self.update, query=self.query)


## Document.ensure_index ##

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


class BaseDocumentSubclassTest(object):

    def setup(self):
        class MyDoc(Document):
            collection = Dingus('collection')
            database = Dingus('database')
        self.MyDoc = MyDoc

    def teardown(self):
        pass


class BaseFindOne(BaseDocumentSubclassTest):

    def setup(self):
        BaseDocumentSubclassTest.setup(self)
        self.MyDoc.check_query_sharding = Dingus('check_query_sharding')

    def should_return_find_one_from_collection(self):
        assert self.MyDoc.collection.calls('find_one').once()
        assert self.returned == self.MyDoc.collection.find_one()


class BaseFindOneWithoutGlobalQuery(BaseFindOne):

    def should_check_query_sharding(self):
        assert self.MyDoc.check_query_sharding.calls('()', self.spec)


class WhenFindingOneWithoutSpec(BaseFindOneWithoutGlobalQuery):

    def setup(self):
        BaseFindOneWithoutGlobalQuery.setup(self)
        self.spec = None

        self.returned = self.MyDoc.find_one()

    def should_find_one_on_collection(self):
        assert self.MyDoc.collection.calls(
            'find_one', None, as_class=self.MyDoc)


class WhenFindingOneWithSpec(BaseFindOneWithoutGlobalQuery):

    def setup(self):
        BaseFindOneWithoutGlobalQuery.setup(self)
        self.spec = Dingus()

        self.returned = self.MyDoc.find_one(self.spec)

    def should_find_one_with_spec(self):
        assert self.MyDoc.collection.calls(
            'find_one', self.spec, as_class=self.MyDoc)


class WhenFindingOneWithSpecAndKeywords(BaseFindOneWithoutGlobalQuery):

    def setup(self):
        BaseFindOneWithoutGlobalQuery.setup(self)
        self.spec = Dingus()
        self.kwargs = {'foo': Dingus(), 'bar': Dingus()}

        self.returned = self.MyDoc.find_one(self.spec, **self.kwargs)

    def should_find_one_with_spec(self):
        assert self.MyDoc.collection.calls(
            'find_one', self.spec, as_class=self.MyDoc, **self.kwargs)


class WhenFindingOneAndAllowingGlobal(BaseFindOne):

    def setup(self):
        BaseFindOne.setup(self)
        self.spec = Dingus()

        self.returned = self.MyDoc.find_one(self.spec, allow_global=True)

    def should_not_check_query(self):
        assert not self.MyDoc.check_query_sharding.calls('()')


class BaseFind(BaseDocumentSubclassTest):

    def setup(self):
        BaseDocumentSubclassTest.setup(self)
        self.MyDoc.check_query_sharding = Dingus('check_query_sharding')

    def should_return_find_from_collection(self):
        assert self.MyDoc.collection.calls('find').once()
        assert self.returned == self.MyDoc.collection.find()


class BaseFindWithoutGlobalQuery(BaseFind):

    def should_check_query_sharding(self):
        assert self.MyDoc.check_query_sharding.calls('()', self.spec)


class WhenFindingWithoutSpec(BaseFindWithoutGlobalQuery):

    def setup(self):
        BaseFindWithoutGlobalQuery.setup(self)
        self.spec = None

        self.returned = self.MyDoc.find()

    def should_find_on_collection(self):
        assert self.MyDoc.collection.calls(
            'find', None, as_class=self.MyDoc)


class WhenFindingWithSpec(BaseFindWithoutGlobalQuery):

    def setup(self):
        BaseFindWithoutGlobalQuery.setup(self)
        self.spec = Dingus()

        self.returned = self.MyDoc.find(self.spec)

    def should_find_with_spec(self):
        assert self.MyDoc.collection.calls(
            'find', self.spec, as_class=self.MyDoc)


class WhenFindingWithSpecAndKeywords(BaseFindWithoutGlobalQuery):

    def setup(self):
        BaseFindWithoutGlobalQuery.setup(self)
        self.spec = Dingus()
        self.kwargs = {'foo': Dingus(), 'bar': Dingus()}

        self.returned = self.MyDoc.find(self.spec, **self.kwargs)

    def should_find_with_spec(self):
        assert self.MyDoc.collection.calls(
            'find', self.spec, as_class=self.MyDoc, **self.kwargs)


class WhenFindingAndAllowingGlobal(BaseFind):

    def setup(self):
        BaseFind.setup(self)
        self.spec = Dingus()

        self.returned = self.MyDoc.find(self.spec, allow_global=True)

    def should_not_check_query(self):
        assert not self.MyDoc.check_query_sharding.calls('()')


## Document.find_and_modify ##


class BaseFindAndModify(BaseDocumentSubclassTest):

    def setup(self):
        BaseDocumentSubclassTest.setup(self)
        self.query = Dingus('query')
        self.update = Dingus('update')
        self.kwargs = {'foo': Dingus('foo'), 'bar': Dingus('bar')}
        self.MyDoc.check_query_sharding = Dingus('check_query_sharding')
        self.MyDoc.validate = Dingus('validate')
        self.MyDoc.__init__ = Dingus('__init__', return_value=None)
        mod.is_update_modifier = Dingus('is_update_modifier')
        mod.validate_update_modifier = Dingus('validate_update_modifier')

    def teardown(self):
        reload(mod)

    def should_check_if_is_update_modifier(self):
        assert mod.is_update_modifier.calls('()', self.update)


class PropertyAllowGlobalIsFalse(object):

    def should_check_query_sharding(self):
        assert self.MyDoc.check_query_sharding.calls('()', self.query)


class PropertyAllowGlobalIsTrue(object):

    def should_not_check_query_sharding(self):
        assert not self.MyDoc.check_query_sharding.calls('()')


class PropertyFindAndModifySuceeds(object):

    def should_run_findandmodify_command(self):
        assert self.MyDoc.database.calls(
            'command', 'findandmodify',
            self.MyDoc.collection.name, query=self.query, update=self.update,
            **self.kwargs)

    def should_wrap_result_in_document_type(self):
        assert self.MyDoc.database.calls('command').once()
        assert self.MyDoc.__init__.calls(
            '()', self.MyDoc.database.command()['value'])

    def should_return_new_document(self):
        assert isinstance(self.returned, self.MyDoc)


class PropertyFindAndModifyOperationFails(object):

    def should_return_none(self):
        assert self.returned is None


class PropertyFindAndModifyWithUpdateModifier(object):

    def should_validate_update_modifier(self):
        assert mod.validate_update_modifier.calls(
            '()', self.update, self.MyDoc.structure)


class PropertyFindAndModifyWithFullDocumentReplacement(object):

    def should_create_new_MyDoc_instance(self):
        assert self.MyDoc.__init__.calls('()', self.update)

    def should_validate_new_instance(self):
        assert self.MyDoc.validate.calls('()')


class TestFindAndModifyWithUpdateModifier(
    BaseFindAndModify,
    PropertyAllowGlobalIsFalse,
    PropertyFindAndModifyWithUpdateModifier,
    ):

    def setup(self):
        BaseFindAndModify.setup(self)
        mod.is_update_modifier.return_value = True

        self.returned = self.MyDoc.find_and_modify(
            self.query, self.update, **self.kwargs)


class TestFindAndModifyWithUpdateModifierAndAllowingGlobalQueries(
    BaseFindAndModify,
    PropertyAllowGlobalIsTrue,
    PropertyFindAndModifyWithUpdateModifier,
    ):

    def setup(self):
        BaseFindAndModify.setup(self)
        mod.is_update_modifier.return_value = True

        self.returned = self.MyDoc.find_and_modify(
            self.query, self.update, allow_global=True, **self.kwargs)


class TestFindAndModifyWithFullDocumentReplacement(
    BaseFindAndModify,
    PropertyAllowGlobalIsFalse,
    PropertyFindAndModifyWithFullDocumentReplacement,
    ):

    def setup(self):
        BaseFindAndModify.setup(self)
        mod.is_update_modifier.return_value = False

        self.returned = self.MyDoc.find_and_modify(
            self.query, self.update, **self.kwargs)


class TestFindAndModifyOperationFailsWhenAllowGlobalIsFalse(
    BaseFindAndModify,
    PropertyAllowGlobalIsFalse,
    PropertyFindAndModifyOperationFails,
    ):

    def setup(self):
        BaseFindAndModify.setup(self)
        self.MyDoc.database.command = exception_raiser(
            OperationFailure(Dingus()))

        self.returned = self.MyDoc.find_and_modify(
            self.query, self.update, **self.kwargs)


class TestFindAndModifyAllowingGlobal(
    BaseFindAndModify,
    PropertyAllowGlobalIsTrue,
    PropertyFindAndModifySuceeds,
    ):

    def setup(self):
        BaseFindAndModify.setup(self)

        self.returned = self.MyDoc.find_and_modify(
            self.query, self.update, allow_global=True, **self.kwargs)


## Document.update ##

class BaseUpdate(BaseDocumentSubclassTest):

    def setup(self):
        BaseDocumentSubclassTest.setup(self)
        self.spec = Dingus('spec')
        self.document = Dingus('document')
        self.kwargs = {'foo': Dingus('foo'), 'bar': Dingus('bar')}
        self.MyDoc.check_query_sharding = Dingus('check_query_sharding')

    def should_update_collection(self):
        assert self.MyDoc.collection.calls(
            'update', self.spec, self.document, **self.kwargs)

    def should_return_result_of_update(self):
        assert self.MyDoc.collection.call('update').once()
        assert self.returned == self.MyDoc.collection.update()


class BaseDocumentIsValidUpdateModifier(BaseUpdate):

    def setup(self):
        BaseUpdate.setup(self)
        mod.is_update_modifier = Dingus('is_update_modifier', return_value=True)
        mod.validate_update_modifier = Dingus('validate_update_modifier')

    def teardown(self):
        BaseUpdate.teardown(self)
        reload(mod)

    def should_check_if_is_update_modifier(self):
        assert mod.is_update_modifier.calls('()', self.document)

    def should_validate_update_modifier(self):
        assert mod.validate_update_modifier.calls(
            '()', self.document, self.MyDoc.structure)


class WhenNotAllowingGlobalQueries(BaseDocumentIsValidUpdateModifier):

    def setup(self):
        BaseDocumentIsValidUpdateModifier.setup(self)
        
        self.returned = self.MyDoc.update(
            self.spec, self.document, **self.kwargs)

    def should_check_query_sharding(self):
        assert self.MyDoc.check_query_sharding.calls('()', self.spec)


class WhenAllowingGlobalQueries(BaseDocumentIsValidUpdateModifier):

    def setup(self):
        BaseDocumentIsValidUpdateModifier.setup(self)

        self.returned = self.MyDoc.update(
            self.spec, self.document, allow_global=True, **self.kwargs)

    def should_check_query_sharding(self):
        assert not self.MyDoc.check_query_sharding.calls('()')


class WhenMakingFullDocumentUpdate(BaseUpdate):

    def setup(self):
        BaseUpdate.setup(self)
        mod.is_update_modifier = Dingus('is_update_modifier', return_value=False)
        self.MyDoc.__init__ = Dingus('__init__', return_value=None)
        self.MyDoc.validate = Dingus('validate')
        self.returned = self.MyDoc.update(
            self.spec, self.document, allow_global=True, **self.kwargs)

    def should_validate_new_value(self):
        assert self.MyDoc.validate.calls('()')

    def should_create_new_MyDoc_with_document(self):
        assert self.MyDoc.__init__.calls('()', self.document)


## Document.remove ##

class BaseRemove(BaseDocumentSubclassTest):

    def setup(self):
        BaseDocumentSubclassTest.setup(self)
        self.MyDoc.check_query_sharding = Dingus('check_query_sharding')
        self.query = self.spec = Dingus('spec')


class PropertyRemovingFromCollection(object):

    def should_remove_from_collection(self):
        assert self.MyDoc.collection.calls('remove', self.spec)

    def should_return_result(self):
        assert self.MyDoc.collection.calls('remove').once()
        assert self.returned == self.MyDoc.collection.remove()


class PropertyRemovingFromCollectionWithKWArgs(
    PropertyRemovingFromCollection):

    def should_remove_from_collection_with_kwargs(self):
        assert self.MyDoc.collection.calls(
            'remove', self.spec, **self.kwargs)


class TestRemoveWithAllowGlobalFalse(
    BaseRemove,
    PropertyAllowGlobalIsFalse,
    PropertyRemovingFromCollection,
    ):

    def setup(self):
        BaseRemove.setup(self)
        self.returned = self.MyDoc.remove(self.spec)


class TestRemoveWithAllowGlobalTrue(
    BaseRemove,
    PropertyAllowGlobalIsTrue,
    PropertyRemovingFromCollection,
    ):

    def setup(self):
        BaseRemove.setup(self)
        self.returned = self.MyDoc.remove(self.spec, allow_global=True)


class TestRemoveWithAllowGlobalFalseAndKWArgs(
    BaseRemove,
    PropertyAllowGlobalIsTrue,
    PropertyRemovingFromCollectionWithKWArgs,
    ):

    def setup(self):
        BaseRemove.setup(self)
        self.kwargs = dict(safe=True, w=3, j=True)
        self.returned = self.MyDoc.remove(
            self.spec, allow_global=True, **self.kwargs)


class TestRemoveWithAllowGlobalTrueAndKWArgs(
    BaseRemove,
    PropertyAllowGlobalIsTrue,
    PropertyRemovingFromCollectionWithKWArgs,
    ):

    def setup(self):
        BaseRemove.setup(self)
        self.kwargs = dict(safe=True, w=3, j=True)
        self.returned = self.MyDoc.remove(
            self.spec, allow_global=True, **self.kwargs)


## Document.check_query_sharding ##

class WhenCheckingQuerySharding(BaseDocumentSubclassTest):

    def setup(self):
        BaseDocumentSubclassTest.setup(self)
        self.MyDoc.shard_index = {'fields': ['foo', 'bar']}
        self.spec = {'foo': Dingus(), 'bar': Dingus()}

        self.MyDoc.check_query_sharding(self.spec)

    def should_not_crash(self):
        pass


class WhenShardIndexNotSpecified(BaseDocumentSubclassTest):

    def setup(self):
        BaseDocumentSubclassTest.setup(self)
        self.MyDoc.shard_index = None
        self.spec = {'foo': Dingus(), 'bar': Dingus()}

        self.MyDoc.check_query_sharding(self.spec)

    def should_not_crash(self):
        pass


class WhenShardIndexNotSpecified(BaseDocumentSubclassTest):

    def setup(self):
        BaseDocumentSubclassTest.setup(self)
        self.MyDoc.shard_index = {'fields': ['biz']}
        self.spec = {'foo': Dingus()}

    def should_raise_global_query_exception(self):
        assert_raises(
            GlobalQueryException, self.MyDoc.check_query_sharding, self.spec)


class BaseShardKeyGetterTest(BaseDocumentSubclassTest):

    def setup(self):
        BaseDocumentSubclassTest.setup(self)
        self.doc = self.MyDoc({
            'foo': Dingus('foo'),
            'bar': Dingus('bar'),
            'biz': Dingus('biz')
        })


class WhenShardKeyNotSet(BaseShardKeyGetterTest):

    def setup(self):
        BaseShardKeyGetterTest.setup(self)

        self.returned = self.doc.shard_key

    def should_return_empty_dict(self):
        assert self.returned == {}


class WhenShardKeyIsSet(BaseShardKeyGetterTest):

    def setup(self):
        BaseShardKeyGetterTest.setup(self)
        self.MyDoc.shard_index = {
            'fields': ['foo', 'bar'],
            'shard_key': True,
        }

        self.returned = self.doc.shard_key

    def should_return_shard_keys_with_values(self):
        assert self.returned == {'foo': self.doc['foo'], 'bar': self.doc['bar']}
