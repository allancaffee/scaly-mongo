from dingus import Dingus
from nose.tools import assert_raises

from scalymongo.helpers import *


## is_update_modifier ##

class WhenDocIsEmpty(object):

    def setup(self):
        self.returned = is_update_modifier({})

    def should_return_false(self):
        assert self.returned is False


class WhenDocContainsNoModifierFields(object):

    def setup(self):
        self.returned = is_update_modifier({'foo': Dingus(), 'bar': Dingus()})

    def should_return_false(self):
        assert self.returned is False


class WhenDocContainsModifierFields(object):

    def setup(self):
        self.returned = is_update_modifier({'foo': Dingus(), 'bar': Dingus()})

    def should_return_false(self):
        assert self.returned is False

####
## value_or_result
####

def when_potential_is_not_callable_should_return_potential():
    assert value_or_result(5) == 5

def when_potential_is_callable_should_return_result():
    d = Dingus('d')
    assert value_or_result(d) == d()

####
## ConversionDict
####

class DescribeConversionDictInit(object):

    def setup(self):
        self.content = {'x': Dingus()}
        self.conversions = Dingus('conversions')

        self.doc = ConversionDict(self.content, self.conversions)

    def should_save_conversions(self):
        assert self.doc._conversions == self.conversions

    def should_save_content(self):
        assert self.doc == self.content


class PropertyRetrievingX(object):

    def should_call_x_conversion(self):
        assert self.x_conversion.calls('()', self.x_value)

    def should_return_converted_value(self):
        assert self.x_conversion.calls('()').once()
        assert self.returned == self.x_conversion()


class PropertyRetrievingY(object):

    def should_return_y_value(self):
        assert self.returned == self.y_value


class BaseConversionDictTest(object):

    def setup(self):
        self.x_value = Dingus('x_value')
        self.y_value = Dingus('y_value')
        self.x_conversion = Dingus('x_conversion')
        content = {'x': self.x_value, 'y': self.y_value}
        conversions = {'x': self.x_conversion}
        self.conversion_dict = ConversionDict(content, conversions)


class WhenGettingItemX(
    BaseConversionDictTest,
    PropertyRetrievingX,
    ):

    def setup(self):
        BaseConversionDictTest.setup(self)
        self.returned = self.conversion_dict['x']


class WhenGettingAttrX(
    BaseConversionDictTest,
    PropertyRetrievingX,
    ):

    def setup(self):
        BaseConversionDictTest.setup(self)
        self.returned = self.conversion_dict.x


class WhenGettingItemY(
    BaseConversionDictTest,
    PropertyRetrievingY,
    ):

    def setup(self):
        BaseConversionDictTest.setup(self)
        self.returned = self.conversion_dict['y']


class WhenGettingItemY(
    BaseConversionDictTest,
    PropertyRetrievingY,
    ):

    def setup(self):
        BaseConversionDictTest.setup(self)
        self.returned = self.conversion_dict.y


class WhenGettingAnEmbeddedDict(object):

    def setup(self):
        self.content = {'a': {'b': Dingus('value')}}
        self.conversions = {'a': {'b': Dingus('conversion')}}
        self.conversion_dict = ConversionDict(self.content, self.conversions)
        self.returned = self.conversion_dict.a

    def should_return_new_conversion_dict(self):
        assert isinstance(self.returned, ConversionDict)

    def should_return_conversion_dict_with_content_of_a(self):
        assert self.returned == self.content['a']

    def should_return_conversion_dict_with_conversions_for_a(self):
        assert self.returned._conversions == self.conversions['a']


## ConversionDict.iteritems ##

class WhenIteratingItems(BaseConversionDictTest):

    def setup(self):
        BaseConversionDictTest.setup(self)

        self.returned = [x for x in self.conversion_dict.iteritems()]

    def should_return_2_items(self):
        assert len(self.returned) == 2

    def should_return_unchanged_y(self):
        assert ('y', self.y_value) in self.returned

    def should_return_converted_x(self):
        assert ('x', self.x_conversion()) in self.returned

    def should_convert_x(self):
        assert self.x_conversion.calls('()', self.x_value)


## ConversionDict.iterkeys ##

class WhenIteratingValues(BaseConversionDictTest):

    def setup(self):
        BaseConversionDictTest.setup(self)

        self.returned = [x for x in self.conversion_dict.itervalues()]

    def should_return_2_items(self):
        assert len(self.returned) == 2

    def should_return_unchanged_y(self):
        assert self.y_value in self.returned

    def should_return_converted_x(self):
        assert self.x_conversion() in self.returned

    def should_convert_x(self):
        assert self.x_conversion.calls('()', self.x_value)
