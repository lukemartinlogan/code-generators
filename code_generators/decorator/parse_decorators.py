from code_generators.cpp.cpp_parse import CppParse
from code_generators.cpp.cpp_parse_node import CppParseNode, CppParseNodeType


class ParseDecorators:
    def __init__(self, decorators, paths):
        self.decorators = {dec.name : dec for dec in decorators}
        self.paths = paths

    def parse(self):
        state = {}
        for path in self.paths:
            parser = CppParse(paths=[path])
            parser.parse()
            self._parse_decorators(parser.get_root_node(), state)
        self._output(state)
        return self

    def _parse_decorators(self, root_node, state):
        i = 0
        while i < root_node.size():
            node = root_node[i]
            if node.node_type == CppParseNodeType.FUNCTION_DEF:
                self._parse_function(node, state)
            elif node.node_type == CppParseNodeType.CLASS_DEFN:
                self._parse_decorators(node, state)
            elif node.node_type == CppParseNodeType.NAMESPACE_DEFN:
                self._parse_decorators(node, state)
            elif node.node_type == CppParseNodeType.BODY:
                self._parse_decorators(node, state)
            i += 1

    def _parse_function(self, func_node, state):
        for spec in func_node.specifiers:
            if spec in self.decorators:
                dec = self.decorators[spec]
                for state_req in dec.state_requirements:
                    if state_req not in state:
                        state[state_req] = []
                self.decorators[spec].generate(func_node, state)
                return

    def _output(self, state):
        for path, lines in state.items():
            with open(path, 'w') as fp:
                fp.write("\n".join(lines))
