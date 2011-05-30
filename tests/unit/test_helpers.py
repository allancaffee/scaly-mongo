from dingus import Dingus

from scalymongo.helpers import *


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
