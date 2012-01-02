from deterministic_dingus import DingusWhitelistTestCase, Dingus, DeterministicDingus

from scalymongo.cursor import Cursor
import scalymongo.cursor as mod


class BaseCursorTestCase(DingusWhitelistTestCase):

    module = mod
    additional_mocks = ['wrapped_cursor']

    def setup(self):
        DingusWhitelistTestCase.setup(self)
        self.document_type = DeterministicDingus('document_type')

        self.cursor = Cursor(self.wrapped_cursor, self.document_type)


####
##
## Cursor.__init__
##
####

class DescribeCursorInit(BaseCursorTestCase):

    def should_save_wrapped_cursor(self):
        assert self.cursor._Cursor__wrapped_cursor is self.wrapped_cursor

    def should_save_document_type(self):
        assert self.cursor._Cursor__document_type is self.document_type


####
##
## Cursor.__getitem__
##
####

class WhenGettingSingleIndex(BaseCursorTestCase):

    additional_mocks = ['index']

    def setup(self):
        BaseCursorTestCase.setup(self)

        self.returned = self.cursor[self.index]

    def should_return_wrapped_document(self):
        assert self.returned is self.document_type(self.wrapped_cursor[self.index])


class WhenGettingSlice(BaseCursorTestCase):

    module_mocks = ['Cursor']
    additional_mocks = ['start', 'stop']

    def setup(self):
        BaseCursorTestCase.setup(self)
        self.module.Cursor = DeterministicDingus('Cursor')

        self.returned = self.cursor[self.start:self.stop]

    def should_return_new_Cursor_from_result(self):
        assert self.returned is mod.Cursor(
            self.wrapped_cursor[self.start:self.stop], self.document_type)


####
##
## Cursor.next
##
####

class WhenGettingNext(BaseCursorTestCase):

    def setup(self):
        BaseCursorTestCase.setup(self)

        self.returned = self.cursor.next()

    def should_return_wrapped_document(self):
        assert self.returned is self.document_type(self.wrapped_cursor.next())


####
##
## Cursor.*
##
####

class BaseWrappedMethod(BaseCursorTestCase):

    module_mocks = ['Cursor']
    additional_mocks = ['arg1', 'arg2', 'kwarg1', 'kwarg2']

    def setup(self):
        BaseCursorTestCase.setup(self)
        self.module.Cursor = DeterministicDingus('Cursor')
        self.method = getattr(self.cursor, self.method_name)
        self.wrapped_method = getattr(self.wrapped_cursor, self.method_name)

        self.returned = self.method(
            self.arg1, self.arg2, kwarg1=self.kwarg1, kwarg2=self.kwarg2)

    def should_return_wrapped_cursor(self):
        assert self.returned is self.module.Cursor(
            self.wrapped_method(), self.document_type)

    def should_call_wrapped_method(self):
        assert self.wrapped_method.calls(
            '()', self.arg1, self.arg2, kwarg1=self.kwarg1, kwarg2=self.kwarg2)


class DescribeBatchSize(BaseWrappedMethod):

    method_name = 'batch_size'


class DescribeClone(BaseWrappedMethod):

    method_name = 'clone'


class DescribeHint(BaseWrappedMethod):

    method_name = 'hint'


class DescribeLimit(BaseWrappedMethod):

    method_name = 'limit'


class DescribeMaxScan(BaseWrappedMethod):

    method_name = 'max_scan'


class DescribeRewind(BaseWrappedMethod):

    method_name = 'rewind'


class DescribeSkip(BaseWrappedMethod):

    method_name = 'skip'


class DescribeSort(BaseWrappedMethod):

    method_name = 'sort'


class DescribeWhere(BaseWrappedMethod):

    method_name = 'where'


class WhenGettingOtherMethodAndAtts(BaseCursorTestCase):

    def should_return_cursor_attrs(self):
        attrs = [
            'alive',
            'collection',
            'count',
            'distinct',
            'explain',
        ]
        for attr in attrs:
            assert getattr(self.cursor, attr) \
                   == getattr(self.wrapped_cursor, attr)
