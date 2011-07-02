from dingus import Dingus

from scalymongo.structure_walker import StructureWalker


class BaseStructureWalker(object):

    @classmethod
    def setup_class(self):
        self.field_validator = Dingus('field_validator')
        self.structure_walker = StructureWalker(self.field_validator)


class WhenWalkingSimpleStructure(BaseStructureWalker):

    @classmethod
    def setup_class(self):
        BaseStructureWalker.setup_class()
        self.body = {'int': 1, 'float': 1.1}
        self.structure = {'int': int, 'float': float}
        self.structure_walker.walk_dict(self.body, self.structure)

    def should_visit_int(self):
        assert self.field_validator.calls('()', 'int', 1, int)

    def should_visit_float(self):
        assert self.field_validator.calls('()', 'float', 1.1, float)


class WhenWalkingStructureWithEmbeddedDict(BaseStructureWalker):

    @classmethod
    def setup_class(self):
        BaseStructureWalker.setup_class()
        self.value = Dingus('value')
        self.type = Dingus('type')
        self.body = {'x': {'y': {'z': self.value}}}
        self.structure = {'x': {'y': {'z': self.type}}}
        self.structure_walker.walk_dict(self.body, self.structure)

    def should_visit_x_y_z(self):
        assert self.field_validator.calls('()', 'x.y.z', self.value, self.type)

    def should_visit_exactly_one_field(self):
        assert self.field_validator.calls('()').once()


class WhenWalkingStructureWithListValue(BaseStructureWalker):

    @classmethod
    def setup_class(self):
        BaseStructureWalker.setup_class()
        self.values = [Dingus('value_0'), Dingus('value_1')]
        self.type = Dingus('type')
        self.body = {'x': self.values}
        self.structure = {'x': [self.type]}
        self.structure_walker.walk_dict(self.body, self.structure)

    def should_visit_x_0(self):
        assert self.field_validator.calls('()', 'x.0', self.values[0], self.type)

    def should_visit_x_1(self):
        assert self.field_validator.calls('()', 'x.1', self.values[1], self.type)


class WhenWalkingStructureWithListOfDocuments(BaseStructureWalker):

    @classmethod
    def setup_class(self):
        BaseStructureWalker.setup_class()
        self.value_0_a = Dingus('value_0_a')
        self.value_0_b = Dingus('value_0_b')
        self.value_1_a = Dingus('value_1_a')
        self.value_1_b = Dingus('value_1_b')
        self.type_a = Dingus('type_a')
        self.type_b = Dingus('type_b')
        self.body = {
            'x': [
                {'a': self.value_0_a, 'b': self.value_0_b},
                {'a': self.value_1_a, 'b': self.value_1_b},
            ],
        }
        self.structure = {
            'x': [{
                'a': self.type_a,
                'b': self.type_b,
             }],
        }
        self.structure_walker.walk_dict(self.body, self.structure)

    def should_visit_x_0_a(self):
        assert self.field_validator.calls(
            '()', 'x.0.a', self.value_0_a, self.type_a)

    def should_visit_x_0_b(self):
        assert self.field_validator.calls(
            '()', 'x.0.b', self.value_0_b, self.type_b)

    def should_visit_x_1_a(self):
        assert self.field_validator.calls(
            '()', 'x.1.a', self.value_1_a, self.type_a)

    def should_visit_x_1_b(self):
        assert self.field_validator.calls(
            '()', 'x.1.b', self.value_1_b, self.type_b)

    def should_visit_exactly_4(self):
        assert self.field_validator.calls(
            '()', 'x.1.b', self.value_1_b, self.type_b)
