"""
Gets the initial structure of a C++ text. Identifies:
1. Functions / lambdas defintions (untemplated)
2. Template argument lists
3. Class/struct definitions
4. Namespace declarations

This parsing is not perfect, as we do not go into the complexity of type
checking and preprocessing. This makes some assumptions about the style of the
C++ code.
"""

import re
from .cpp_parse_node import CppParseNode, CppParseNodeType


class CppParse3:
    def __init__(self, parse_tree=None):
        self.parse_tree = parse_tree

    def parse(self):
        self._reparse(self.parse_tree.get_root_node())
        return self

    def _reparse(self, root_node):
        i = 0
        while i < root_node.size():
            node = root_node[i]
            if node.node_type == CppParseNodeType.TEMPLATE_KEYWORD:
                ret = self._parse_template_defn(root_node, i)
                if ret > 0:
                    i = ret
                    continue
            if node.node_type == CppParseNodeType.CLASS_DEFN:
                self._reparse(node)
            elif node.node_type == CppParseNodeType.NAMESPACE_DEFN:
                self._reparse(node)
            elif node.node_type == CppParseNodeType.BODY:
                self._reparse(node)
            i += 1

    def _parse_template_defn(self, root_node, i):
        """
        Converts:
        [COMMENT] [template] [TEMPLATE_PARAMS] [FUNCTION]
        [COMMENT] [template] [TEMPLATE_PARAMS] [CLASS_DEFN]
        Into:
        [FUNCTION] OR
        [CLASS_DEFN]

        i: the index of the "template" keyword"
        """

        i0 = i

        # First node must be "template"
        node = root_node[i]
        if node.node_type != CppParseNodeType.TEMPLATE_KEYWORD:
            return -1
        i += 1

        # Prior node might be "comment"
        if i0 > 0:
            node = root_node[i0 - 1]
            if node.node_type == CppParseNodeType.COMMENT:
                i0 -= 1

        # Next node must be TEMPLATE_PARAMS
        node = root_node[i]
        if node.node_type != CppParseNodeType.TEMPLATE_PARAMS:
            return -1
        tparams_i = i
        i += 1

        # Next node must be FUNCTION
        node = root_node[i]
        if node.node_type == CppParseNodeType.FUNCTION:
            pass
        elif node.node_type == CppParseNodeType.CLASS_DEFN:
            pass
        else:
            return -1
        i += 1
        func_node = node

        # Update FUNCTION node
        func_node.add_child_nodes(root_node, i0, tparams_i)
        root_node.replace_children(func_node, i0, i)
        return i0 + 1

    def get_root_node(self):
        return self.parse_tree.get_root_node()
