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

## AttrDict ##

class BaseAttrDictTest(object):

    def setup(self):
        self.attr_dict = AttrDict()


## AttrDict.__getattr__ ##

class WhenAttrDictHasItemByName(BaseAttrDictTest):

    def setup(self):
        BaseAttrDictTest.setup(self)
        self.by_name = Dingus()
        self.attr_dict['by_name'] = self.by_name

    def should_return_by_name(self):
        assert self.attr_dict.by_name == self.by_name


class WhenAttrDictHasDictItemByName(BaseAttrDictTest):

    def setup(self):
        BaseAttrDictTest.setup(self)
        self.by_name = {'key': Dingus('value')}
        self.attr_dict['by_name'] = self.by_name

        self.returned = self.attr_dict.by_name

    def should_return_new_attr_dict(self):
        assert isinstance(self.attr_dict, AttrDict)

    def should_return_equivalent_dict(self):
        assert self.returned == self.by_name


class WhenAttrDictHasNoItemByName(BaseAttrDictTest):

    def should_raise_attribute_error(self):
        assert_raises(AttributeError, getattr, self.attr_dict, 'by_name')


## AttrDict.__setattr__ ##

class WhenSettingAttrByName(BaseAttrDictTest):

    def setup(self):
        BaseAttrDictTest.setup(self)
        self.by_name = Dingus()
        self.attr_dict.by_name = self.by_name

    def should_return_by_name(self):
        assert self.attr_dict['by_name'] == self.by_name
