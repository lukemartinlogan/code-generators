"""
Two actions
1. Process #define
2. Process #if, #elif, #else, #endif
3. Process #ifdef, #elifdef, #elsedef
4. Process #undef
"""

import re
from .cpp_parse_node import CppParseNode, CppParseNodeType


class CppParse3:
    def __init__(self, parse_tree=None, include_dirs=None, macros=None):
        self.parse_tree = parse_tree
        if include_dirs is None:
            self.include_dirs = []
        if macros is None:
            self.macros = {}
        self.cur_node = None
        for macro_name, macro_val in self.macros.items():
            if isinstance(macro_val, str):
                macro_node = CppParseNode(CppParseNodeType.MACRO_DEF)
                macro_node.make_tok_child(CppParseNodeType.MACRO_BODY,
                                          macro_val, None)
                self.macros[macro_name] = macro_node

    def parse(self):
        self.cur_node = self.get_root_node()
        self._parse(self.cur_node)
        return self

    def _parse(self, root_node):
        i = 0
        while i < root_node.size():
            node = root_node[i]
            if not node.is_one_of(CppParseNodeType.PREPROCESSOR):
                if self._check_if_macro(node):
                    self._parse_macro(root_node, i)
                elif self._check_if_function_macro(node):
                    self._parse_function_macro(root_node, i)
            else:
                preprocess_type = node[0]
                if preprocess_type == '#define':
                    i = self._parse_define(node)
                elif preprocess_type == "#undef":
                    i = self._parse_undefine(node)
                elif preprocess_type == '#pragma':
                    i += 1
                elif preprocess_type == '#error':
                    i += 1
                elif preprocess_type == '#if':
                    next_i = self._parse_if(root_node, i)
                elif preprocess_type == '#ifdef':
                    next_i = self._parse_ifdef(root_node, i)
                elif preprocess_type == '#ifndef':
                    next_i = self._parse_ifdef(root_node, i)
                elif preprocess_type == '#include':
                    i += 1
                elif preprocess_type == '#endif':
                    i += 1

    def _check_if_function_macro(self, root_node):
        """
        Checks if the node equates to a function macro

        :param root_node: the node being checked if macro
        :return:
        """
        if root_node.val not in self.macros:
            return False
        macro_node = self.macros[root_node.val]
        return macro_node.is_one_of(CppParseNodeType.MACRO_DEF)

    def _check_if_macro(self, root_node):
        """
        Checks if the node equates to a macro

        :param root_node: the node being checked if it's a macro
        :return:
        """
        if root_node.val not in self.macros:
            return False
        macro_node = self.macros[root_node.val]
        return macro_node.is_one_of(CppParseNodeType.MACRO_DEF)

    def _find_macro_body(self, root_node):
        """
        Find the BODY keyword in the macro definition

        :param root_node: the macro node
        :return:
        """
        i = 0
        while i < root_node.size():
            node = root_node[i]
            if node.is_one_of(CppParseNodeType.MACRO_BODY):
                return i
            i += 1
        return None


    def _parse_macro(self, root_node, i):
        """
        Replaces root_node[i] with the body of the macro

        :param root_node:
        :return:
        """
        macro_node = self.macros[root_node[i].val]
        root_node.replace_children()

    def _parse_function_macro(self, root_node, i):
        """
        Replaces root_node[i] with the body of the macro. Determines the
        value of the macro parameters and replaces them in the macro body.

        :param root_node:
        :return:
        """

        pass

    def _parse_define(self, root_node, i):
        """
        #define [MACRO_NAME] ...

        :param root_node:
        :param i: the index of the #define in root_node
        :return:
        """
        macro_name = root_node[0].val
        self.macros[macro_name] = root_node
        return i + 1

    def _parse_undefine(self, root_node, i):
        pass

    def _parse_if(self, root_node, i, depth=0):
        return self._parse_generic_if(CppParseNodeType.MACRO_IF,
                                      root_node, i, depth)

    def _parse_ifdef(self, root_node, i, depth=0):
        return self._parse_generic_if(CppParseNodeType.MACRO_IFDEF,
                                      root_node, i, depth)

    def _parse_ifndef(self, root_node, i, depth=0):
        return self._parse_generic_if(CppParseNodeType.MACRO_IFNDEF,
                                      root_node, i, depth)

    def _parse_generic_if(self, if_node_type,
                          root_node, i, depth):
        """
        Makes the #ifdef-elsedef recursively. Then processes it.

        :param root_node: The node parent to the #if
        :param i: the index of #if in the root node
        :return:
        """

        i0 = i
        if_node = CppParseNode(if_node_type)
        if_node.add_child_node(root_node[i0])
        cur_node_tmp = self.cur_node
        if_node[0].add_child_node(CppParseNodeType.BODY)
        self.cur_node = if_node[0]
        i += 1

        while i < root_node.size():
            node = root_node[i]
            if node.is_one_of(CppParseNodeType.PREPROCESSOR):
                preprocess_type = node[0]
                if preprocess_type == '#if':
                    i = self._parse_if(root_node, i, depth + 1)
                elif preprocess_type == '#ifdef':
                    i = self._parse_ifdef(root_node, i, depth + 1)
                elif preprocess_type == 'ifndef':
                    i = self._parse_ifndef(root_node, i, depth + 1)
                elif preprocess_type == 'elif':
                    self.cur_node = node
                elif preprocess_type == '#else':
                    self.cur_node = node
                elif preprocess_type == '#endif':
                    break
            else:
                self.cur_node.add_child_node(node)
            i += 1

        if i == root_node.size():
            self.add_error(root_node[i], "#endif was not found")

        self.cur_node = cur_node_tmp
        if depth == 0:
            root_node.replace_children(if_node, i0, i)
        return i0 + 1

    def _process_include(self, root_node):
        pass

    def get_root_node(self):
        return self.parse_tree.get_root_node()

    def get_style_nodes(self):
        return self.parse_tree.get_style_nodes()

    def add_error(self, node, msg):
        return self.parse_tree.add_error(node, msg)

    def get_errors(self):
        return self.parse_tree.get_errors()
