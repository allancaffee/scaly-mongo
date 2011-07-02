from dingus import Dingus

from scalymongo.schema_operators import *
import scalymongo.schema_operators as mod


## OR ##


class DescribeEvaluateOr(object):

    def setup(self):
        # Use ints to avoid weirdness with the ordering.
        self.arg0 = 1
        self.arg1 = 2
        self.value = Dingus('value')
        mod.isinstance = Dingus('isinstance')
        self.or_ = OR(self.arg0, self.arg1)

        self.returned = self.or_.evaluate(self.value)

    def teardown(self):
        del mod.isinstance

    def should_return_isinstance_result(self):
        assert mod.isinstance.calls('()').once()
        assert self.returned == mod.isinstance()

    def should_call_isinstance_on_value_against_args(self):
        assert mod.isinstance.calls('()', self.value, (self.arg0, self.arg1))


class WhenComparingOrDeclarations(object):

    def should_recognize_equivalent_ors(self):
        assert OR(int, float, long) == OR(int, float, long)

    def should_recognize_different_ordered_args(self):
        assert OR(int, float) == OR(float, int)

    def should_reject_different_ors(self):
        assert not OR(int, float) == OR(int, long)

    def should_reject_invalid_comparison(self):
        assert not OR(int, float) == Dingus()


class WhenRepresentingOr(object):

    def should_use_csv_of_reprs(self):
        assert repr(OR(int, float)) == "<OR <type 'float'>, <type 'int'>>"
        assert repr(OR(int, float, str)) \
               == "<OR <type 'float'>, <type 'int'>, <type 'str'>>"


## IS ##


class DescribeEvaluatorIs(object):

    def setup(self):
        self.arg0 = Dingus()
        self.arg1 = Dingus()
        mod.isinstance = Dingus()
        self.is_ = IS(self.arg0, self.arg1)

    def should_evaluate_arg0_as_true(self):
        assert self.is_.evaluate(self.arg0) is True

    def should_evaluate_arg1_as_true(self):
        assert self.is_.evaluate(self.arg1) is True

    def should_evaluate_others_as_false(self):
        assert self.is_.evaluate(Dingus()) is False


class WhenComparingIsDeclarations(object):

    def should_recognize_identical_args(self):
        assert IS(1, 2) == IS(1, 2)

    def should_recognize_different_order_args(self):
        assert IS(1, 2) == IS(2, 1)

    def should_reject_different_args(self):
        assert not IS(1, 2, 3) == IS(4, 5, 6)

    def should_reject_differet_type_other(self):
        assert not IS(1, 2, 3) == 3


class WhenRepresentingOr(object):

    def should_use_csv_of_reprs(self):
        assert repr(IS(1, 'foo')) == "<IS 1, 'foo'>"
