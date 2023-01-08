from code_generators.decorator.decorator import Decorator


class TestDecorator(Decorator):
    def __init__(self):
        super().__init__("TEST", ["_test.h"])

    def generate(self, func_node, state):
        new_name = func_node.name.replace("Local", "Global")
        text = f"{func_node.type} {new_name}();"
        state["_test.h"].append(text)

