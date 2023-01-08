from code_generators.decorator.test_decorator import TestDecorator
from code_generators.decorator.parse_decorators import ParseDecorators

decorators = [
    TestDecorator()
]

parser = ParseDecorators(decorators, paths=["test.h"])
parser.parse()