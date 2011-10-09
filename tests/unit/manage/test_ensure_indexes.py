from deterministic_dingus import DingusWhitelistTestCase, Dingus
from nose.tools import assert_raises, assert_equals

from scalymongo.manage.ensure_indexes import (
    ensure_indexes,
    main,
    parse_arguments,
)
import scalymongo.manage.ensure_indexes as mod


####
##
## parse_arguments
##
####

class BaseParseArgumentsTestCase(DingusWhitelistTestCase):

    module = mod
    module_mocks = ['OptionParser']
    additional_mocks = ['options']

    def setup(self):
        DingusWhitelistTestCase.setup(self)
        self.parser = self.module.OptionParser()

    def should_set_up_usage_string(self):
        assert self.parser.usage == '%prog MODULE ENDPOINT'

    def should_parse_args(self):
        assert self.parser.calls('parse_args')


class WhenArgumentsParseSuccessfully(BaseParseArgumentsTestCase):

    additional_mocks = ['module_name', 'endpoint']

    def setup(self):
        BaseParseArgumentsTestCase.setup(self)
        self.arguments = (self.module_name, self.endpoint)
        self.parser.parse_args.return_value = (self.options, self.arguments)

        self.returned = parse_arguments()

    def should_return_options_module_name_and_endpoint(self):
        assert_equals(
            self.returned,
            (self.options, self.module_name, self.endpoint),
        )


class WhenWrongNumberOfPositionalArguments(BaseParseArgumentsTestCase):

    additional_mocks = ['arguments']

    def setup(self):
        BaseParseArgumentsTestCase.setup(self)
        self.parser.parse_args.return_value = (self.options, self.arguments)

        assert_raises(SystemExit, parse_arguments)

    def should_print_help(self):
        assert self.parser.calls('print_help')


####
##
## main
##
####

class DescribeParseArguments(DingusWhitelistTestCase):

    module = mod
    module_mocks = [
        'parse_arguments', '__import__', 'Connection', 'ensure_indexes']
    additional_mocks = ['options', 'module_name', 'endpoint']

    def run(self):
        self.module.parse_arguments.return_value = (
            self.options, self.module_name, self.endpoint)

        main()

    def should_import_module(self):
        assert self.module.__import__.calls('()', self.module_name)

    def should_make_Connection(self):
        assert self.module.Connection.calls('()', self.endpoint)

    def should_ensure_indexes(self):
        assert self.module.ensure_indexes.calls('()', self.module.Connection())


####
##
## ensure_indexes
##
####

class DescribeEnsureIndexes(DingusWhitelistTestCase):

    module = mod
    additional_mocks = ['connection', 'model_a', 'model_b']

    def run(self):
        self.connection.models = [self.model_a, self.model_b]

        ensure_indexes(self.connection)

    def should_ensure_indexes_on_each_model(self):
        assert self.model_a.calls('ensure_indexes', background=True)
        assert self.model_b.calls('ensure_indexes', background=True)
