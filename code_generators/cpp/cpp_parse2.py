"""
Parses two main things:
1. Context-free groupings (parens, braces, brackets)
2. Multi-token Operators (++, --, ::, etc.)
"""

import re
from .cpp_parse_node import CppParseNode, CppParseNodeType
from .cpp_parse_base import CppParseBase


class CppParse2(CppParseBase):
    def __init__(self, parse_tree=None, state=None):
        self.parse_tree = parse_tree
        self.cur_node = None

    def parse(self):
        self.cur_node = self.get_root_node()
        self._parse(self.cur_node)
        return self

    def _parse(self, root_node, i=0, term=None):
        while i < root_node.size():
            node = root_node[i]
            if term and node[i].is_one_of(term):
                return i
            if node.is_one_of(CppParseNodeType.PAREN_LEFT):
                self._parse_parens(root_node, i)
            elif node.is_one_of(CppParseNodeType.BRACKET_LEFT):
                self._parse_brackets(root_node, i)
            elif node.is_one_of(CppParseNodeType.BRACE_LEFT):
                self._parse_braces(root_node, i)
            elif node.is_one_of(CppParseNodeType.COLON):
                i = self._parse_ns_sep(root_node, i)
            elif node.is_one_of(CppParseNodeType.OP):
                i = self._parse_op(root_node, i)
            else:
                i += 1
        return i

    def _parse_parens(self, root_node, i):
        return self._parse_grouping(root_node, i,
                                    CppParseNodeType.PARENTHESIS,
                                    CppParseNodeType.PAREN_RIGHT)

    def _parse_brackets(self, root_node, i):
        return self._parse_grouping(root_node, i,
                                    CppParseNodeType.BRACKETS,
                                    CppParseNodeType.BRACKET_RIGHT)

    def _parse_braces(self, root_node, i):
        return self._parse_grouping(root_node, i,
                                    CppParseNodeType.BRACES,
                                    CppParseNodeType.BRACE_RIGHT)

    def _parse_ns_sep(self, root_node, i):
        if self._pattern_matches(root_node, i, ':', ':'):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.NS_SEP)
        return i + 1

    def _parse_op(self, root_node, i):
        # Arithmetic operators
        if self._pattern_matches(root_node, i, '+', '+'):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '-', '-'):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '+', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '-', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '*', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '/', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '%', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)

        # Relational operators
        elif self._pattern_matches(root_node, i, '=', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '!', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '<', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '>', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)

        # Bitwise operators
        elif self._pattern_matches(root_node, i, '&', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '|', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '^', '='):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '<', '<'):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '>', '>'):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '<', '<', '='):
            return self._parse_pattern(root_node, i, 3, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '>', '>', '='):
            return self._parse_pattern(root_node, i, 3, CppParseNodeType.OP)

        # Logical operators
        elif self._pattern_matches(root_node, i, '&', '&'):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)
        elif self._pattern_matches(root_node, i, '|', '|'):
            return self._parse_pattern(root_node, i, 2, CppParseNodeType.OP)

        return i + 1

    def _pattern_matches(self, root_node, i, *vals):
        for val in vals:
            if root_node[i].val != val:
                return False
        return True
    
    def _parse_pattern(self, root_node, i, count, node_type):
        i0 = i
        new_node = CppParseNode(node_type)
        for k in range(count):
            new_node.add_child_node(root_node[i])
            i += 1
        new_node.join(inplace=True, destroy_children=True)
        root_node.replace_children(new_node, i0, i - 1)
        return i

    def get_root_node(self):
        return self.parse_tree.get_root_node()

    def get_style_nodes(self):
        return self.parse_tree.get_style_nodes()

    def add_error(self, node, msg):
        return self.parse_tree.add_error(node, msg)

    def get_errors(self):
        return self.parse_tree.get_errors()
