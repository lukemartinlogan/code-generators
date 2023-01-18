from code_generators.cpp.cpp_parse import CppParse
from code_generators.cpp.cpp_parse_node import CppParseNodeType


class Api:
    def __init__(self, text):
        self.parse_tree = CppParse(text=text).parse()
        self._parse_api(self.parse_tree.get_root_node())
        self.params = []
        self.func_name = None
        self.func_ret = None

    def _parse_api(self, root_node):
        i = 0
        while i < root_node.size():
            node = root_node[i]
            if node.node_type == CppParseNodeType.FUNCTION_DEF:
                self._parse_function(node)
                break
            i += 1

    def _parse_function(self, func_node):
        i = 0
        self.func_name = func_node.name
        self.func_ret = func_node.type
        while i < func_node.size():
            node = func_node[i]
            if node.node_type == CppParseNodeType.PARAMS:
                self._parse_args(node)
                break
            i += 1

    def _parse_args(self, root_node):
        i = 0
        while i < root_node.size():
            node = root_node[i]
            param = {}
            param.type = node[0].val
            param.name = node[1].val
            self.params.append(param)

    def get_args(self):
        l = [f"{p.type} {p.name}" for p in self.params]
        return ", ".join(l)

    def pass_args(self):
        l = [f"{p.name}" for p in self.params]
        return ", ".join(l)
