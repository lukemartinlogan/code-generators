"""
Tokenizes a C/C++ file and parses using only basic syntax. It is used to
infer the true nature of the file for simple code generation.
"""

import re
from .cpp_parse_node import CppParseNode, CppParseNodeType


class CppParse1:
    def __init__(self, lex=None):
        self.lex = lex
        self.root_node = None
        self.cur_node = None

    def _parse_text(self):
        self.root_node = CppParseNode()
        self.cur_node = self.root_node
        self._parse_toks(self.lex.toks)

    def _parse_toks(self, toks, i=0, term=None):
        while i < len(toks):
            tok = toks[i]
            if term is not None and tok == term:
                return i + 1
            if tok == '\"':
                i = self._parse_string(toks, i)
            elif tok == '\'':
                i = self._parse_char(toks, i)
            elif tok == '/' and toks[i+1] == '*':
                i = self._parse_ml_comment(toks, i)
            elif tok == '/' and toks[i+1] == '/':
                i = self._parse_sl_comment(toks, i)
            elif self._is_whitespace(toks, i):
                i = self._parse_whitespace(toks, i)
            elif tok == '#':
                i = self._parse_preprocessor(toks, i)
            elif tok == '(':
                i = self._parse_parens(toks, i)
            elif tok == '[':
                i = self._parse_bracket(toks, i)
            elif tok == '<':
                i = self._parse_angle_bracket(toks, i)
            elif tok == '{':
                i = self._parse_brace(toks, i)
            elif tok == ':':
                i = self._parse_colon(toks, i)
            elif self._is_op(toks, i):
                i = self._parse_op(toks, i)
            else:
                i = self._parse_name(toks, i)

    def _parse_ml_comment(self, toks, i):
        """
        Parses a multi-line comment (ends with */)

        i: the index of the starting / of the /*
        """
        i += 2
        self.cur_node.add_child(CppParseNodeType.COMMENT)
        self.cur_node = self.cur_node.prior_child()
        while i < len(toks) - 1:
            tok1 = toks[i]
            tok2 = toks[i+1]
            if tok1 == '*' and tok2 == '/':
                self.cur_node.val = self.cur_node.join()
                self.cur_node = self.cur_node.parent
                return i + 2
            self.cur_node.add_child(CppParseNodeType.TEXT, tok1)
            i += 1
        raise Exception("Couldn't find the end */ of the multi-line comment")

    def _parse_sl_comment(self, toks, i):
        """
        Parses a single-line comment (ends with \n)

        i: the index of the starting / of the //
        """
        i += 2
        self.cur_node.add_child(CppParseNodeType.COMMENT)
        self.cur_node = self.cur_node.prior_child()
        while i < len(toks):
            tok = toks[i]
            if '\n' in tok:
                break
            self.cur_node.add_child(CppParseNodeType.TEXT, tok)
            i += 1
        self.cur_node.val = self.cur_node.join()
        self.cur_node = self.cur_node.parent
        return i + 1

    @staticmethod
    def _is_string(toks, i):
        is_str = toks[i] == '\"'
        if i == 0:
            return is_str
        if toks[i - 1] == '\\':
            return False
        return is_str

    @staticmethod
    def _is_multiline_sep(toks, i):
        # Multi-line strings and preprocessors end in \
        if i >= len(toks):
            return False
        if i == 0:
            return False
        if toks[i] == '\\' and toks[i - 1] != '\\':
            return True

    @staticmethod
    def _is_char(toks, i):
        is_char = toks[i] == '\''
        if i == 0:
            return is_char
        if toks[i - 1] == '\\':
            return False
        return is_char

    def _is_whitespace(self, toks, i):
        return re.match('\s+', toks[i])

    def _parse_whitespace(self, toks, i):
        del toks[i]
        return i

    def _parse_string(self, toks, i):
        """
        Parse to the end of a C++ string.

        :param i: the index of the \" token
        :return: the index of the token after the string ends
        """
        i += 1
        self.cur_node.add_child(CppParseNodeType.STRING)
        self.cur_node = self.cur_node.prior_child()
        while i < len(toks):
            if self._is_string(toks, i):
                self.cur_node.val = self.cur_node.join()
                self.cur_node = self.cur_node.parent
                return i + 1
            if self._is_multiline_sep(toks, i):
                del toks[i]
                continue
            self.cur_node.add_child(CppParseNodeType.TEXT, toks[i])
            i += 1
        raise Exception("Could not find end of string")

    def _parse_char(self, toks, i):
        """
        Parse to the end of a C++ string.

        :param i: the index of the \' token
        :return: the index of the token after the char ends
        """
        i += 1
        self.cur_node.add_child(CppParseNodeType.CHAR)
        self.cur_node = self.cur_node.prior_child()
        while i < len(toks):
            if self._is_char(toks, i):
                self.cur_node.val = self.cur_node.join()
                self.cur_node = self.cur_node.parent
                return i + 1
            self.cur_node.add_child(CppParseNodeType.TEXT, toks[i])
            i += 1
        raise Exception("Could not find end of char")

    def _parse_preprocessor(self, toks, i):
        i += 1
        self.cur_node.add_child(CppParseNodeType.PREPROCESSOR)
        self.cur_node = self.cur_node.prior_child()
        while i < len(toks):
            if '\n' in toks[i]:
                if self._is_multiline_sep(toks, i+1):
                    self.cur_node.val = self.cur_node.join()
                    self.cur_node = self.cur_node.parent
                    break
                break
            i += 1
        return i + 1

    def _parse_grouping(self, toks, i, term, node_type):
        """
        Group everything between starter and terminator recursively.
        """
        self.cur_node.add_child(CppParseNodeType.PARENS)
        self.cur_node = self.cur_node.prior_child()
        next_start = self._parse_toks(toks, i + 1, term=term)
        self.cur_node = self.cur_node.parent
        return next_start

    def _parse_parens(self, toks, i):
        return self._parse_grouping(toks, i, ')', CppParseNodeType.PARENS)

    def _parse_bracket(self, toks, i):
        return self._parse_grouping(toks, i, ']', CppParseNodeType.BRACKETS)

    def _parse_brace(self, toks, i):
        return self._parse_grouping(toks, i, '}', CppParseNodeType.BRACES)

    def _parse_angle_bracket(self, toks, i):
        pass

    def _parse_colon(self, toks, i):
        """
        Could be initializer list, namespace separator, iterator, or
        inheritance
        """
        return i + 1

    def _is_op(self, toks, i):
        return False

    def _parse_op(self, toks, i):
        return i + 1

    def _parse_name(self, toks, i):
        return i + 1
