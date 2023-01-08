"""
Gets the initial structure of a C++ text. Identifies:
1. Functions / lambdas
2. Template definitions and instantiations
"""

import re
from .cpp_parse_node import CppParseNode, CppParseNodeType


class CppParse2:
    def __init__(self, parse_tree=None):
        self.parse_tree = parse_tree

    def parse(self):
        self._reparse(self.parse_tree.get_root_node())
        return self

    def _reparse(self, root_node):
        pass

    def get_root_node(self):
        return self.parse_tree.get_root_node()