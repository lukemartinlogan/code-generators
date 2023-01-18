"""
Identifies:
1. Templated functions + classes
2. Properties of a function (e.g., name and specifier)
3. Properties of a class (e.g., name)
4. Properties of a namespace (e.g., name)

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
        self._reparse(self.get_root_node())
        return self

    def _reparse(self, root_node):
        i = 0
        while i < root_node.size():
            node = root_node[i]
            if node.node_type == CppParseNodeType.FUNCTION_DEF:
                self._parse_function_defn(node)

            if node.node_type == CppParseNodeType.TEMPLATE_KEYWORD:
                ret = self._parse_template_defn(root_node, i)
                if ret > 0:
                    i = ret
                    continue
            elif node.node_type == CppParseNodeType.CLASS_DEFN:
                self._parse_class(node)
                self._reparse(node)
            elif node.node_type == CppParseNodeType.NAMESPACE_DEFN:
                self._parse_namespace(node)
                self._reparse(node)
            elif node.node_type == CppParseNodeType.BODY:
                self._reparse(node)
            i += 1

    def _parse_function_defn(self, func_node):
        """
        Determines properties of a function
        (e.g., function type, name, specifiers)

        [SPECIFIERS] [FUNC_TYPE] [FUNC_NAME] [FUNC_PARAMS]
        """

        # Determine the index of the function params
        i = 0
        while i < func_node.size():
            node = func_node[i]
            if node.node_type == CppParseNodeType.PARAMS:
                break
            i += 1

        # Return if this is simply a function call
        if i < 2:
            node.node_type = CppParseNodeType.FUNCTION_CALL
            return

        # Get the function name
        func_node.name = func_node[i - 1].val

        # Get the function type
        func_node.type = func_node[i - 2].val

        # Get the function specifiers
        func_node.specifiers = []
        for spec in func_node.get_children()[:i-2]:
            if spec.node_type == CppParseNodeType.KEYWORD:
                func_node.specifiers.append(spec.val)
            elif spec.node_type == CppParseNodeType.TEXT:
                func_node.specifiers.append(spec.val)

        # Get the function docstring
        func_node.docstring = ""
        for node in func_node.get_children():
            if node.is_one_of(CppParseNodeType.ML_COMMENT,
                            CppParseNodeType.SL_COMMENT):
                func_node.docstring = node.val
                break

    def _parse_class(self, class_node):
        """
        Determines other properties of a class
        """
        class_node.name = class_node[0].val

    def _parse_namespace(self, ns_node):
        """
        Determines other properties of a namespace
        """
        ns_node.name = ns_node[0].val

    def _parse_template_defn(self, root_node, i):
        """
        Converts:
        [COMMENT] [template] [TEMPLATE_PARAMS] [FUNCTION_DEF]
        [COMMENT] [template] [TEMPLATE_PARAMS] [CLASS_DEFN]
        Into:
        [FUNCTION_DEF] OR
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
            if node.is_one_of(CppParseNodeType.ML_COMMENT,
                            CppParseNodeType.SL_COMMENT):
                i0 -= 1

        # Next node must be TEMPLATE_PARAMS
        node = root_node[i]
        if node.node_type != CppParseNodeType.TEMPLATE_PARAMS:
            return -1
        tparams_i = i
        i += 1

        # Next node must be FUNCTION_DEF
        node = root_node[i]
        if node.node_type == CppParseNodeType.FUNCTION_DEF:
            pass
        elif node.node_type == CppParseNodeType.CLASS_DEFN:
            pass
        else:
            return -1
        i += 1
        func_node = node

        # Update FUNCTION_DEF node
        func_node.add_child_nodes(root_node, i0, tparams_i)
        root_node.replace_children(func_node, i0, i)
        return i0 + 1

    def get_root_node(self):
        return self.parse_tree.get_root_node()

    def get_style_nodes(self):
        return self.parse_tree.get_style_nodes()
