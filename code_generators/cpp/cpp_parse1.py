"""
Gets the initial structure of a C++ text. Identifies:
1. Preprocessor macros
2. Strings/characters
3. Non-angle Groupings (e.g., braces, brackets, parenthesis)
4. Some binary/unary operations
"""

import re
from .cpp_parse_node import CppParseNode, CppParseNodeType


class CppParse1:
    def __init__(self, lex=None):
        self.lex = lex
        self.root_node = None
        self.cur_node = None

    def parse(self):
        self.root_node = CppParseNode()
        self.cur_node = self.root_node
        self._parse_toks(self.lex.toks)
        return self

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
            elif tok == '{':
                i = self._parse_brace(toks, i)
            elif tok == '<' or tok == '>':
                i = self._parse_angle_bracket(toks, i)
            elif tok == ',':
                i = self._parse_comma(toks, i)
            elif tok == ':':
                i = self._parse_colon(toks, i)
            elif tok == ';':
                i = self._parse_semicolon(toks, i)
            elif self._is_keyword(tok):
                i = self._parse_keyword(toks, i)
            elif self._is_op(toks, i):
                i = self._parse_op(toks, i)
            else:
                i = self._parse_text(toks, i)

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
                self.cur_node.join()
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
        self.cur_node.join()
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
                self.cur_node.join()
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
                self.cur_node.join()
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
                    self.cur_node.join()
                    self.cur_node = self.cur_node.parent
                    break
                break
            i += 1
        return i + 1

    def _parse_grouping(self, toks, i, term, node_type):
        """
        Group everything between starter and terminator recursively.
        """
        self.cur_node.add_child(node_type)
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
        if toks[i] == '<':
            self.cur_node.add_child(CppParseNodeType.ANGLE_BRACKET_LEFT)
        else:
            self.cur_node.add_child(CppParseNodeType.ANGLE_BRACKET_RIGHT)
        self.cur_node.val = toks[i]
        return i + 1

    def _parse_comma(self, toks, i):
        return self._parse_single_tok(toks, i, CppParseNodeType.COMMA)

    def _parse_colon(self, toks, i):
        return self._parse_single_tok(toks, i, CppParseNodeType.COLON)

    def _parse_semicolon(self, toks, i):
        return self._parse_single_tok(toks, i, CppParseNodeType.SEMICOLON)

    def _is_op(self, toks, i):
        if toks[i] == '+':
            return True
        if toks[i] == '-':
            return True
        if toks[i] == '*':
            return True
        if toks[i] == '/':
            return True
        if toks[i] == '<':
            return True
        if toks[i] == '>':
            return True
        if toks[i] == '=':
            return True
        if toks[i] == '?':
            return True
        if toks[i] == '%':
            return True
        return False

    def _parse_op(self, toks, i):
        return self._parse_single_tok(toks, i, CppParseNodeType.OP)

    def _parse_text(self, toks, i):
        return self._parse_single_tok(toks, i, CppParseNodeType.TEXT)

    def _is_keyword(self, tok):
        if tok == 'class':
            return True
        elif tok == 'struct':
            return True
        elif tok == 'public':
            return True
        elif tok == 'private':
            return True
        elif tok == 'protected':
            return True
        elif tok == 'namespace':
            return True
        elif tok == 'template':
            return True
        elif tok == 'int':
            return True
        elif tok == 'float':
            return True
        elif tok == 'double':
            return True
        elif tok == 'const':
            return True
        elif tok == 'constexpr':
            return True
        elif tok == 'inline':
            return True
        elif tok == 'static':
            return True
        else:
            return False

    def _parse_keyword(self, toks, i):
        tok = toks[i]
        if tok == 'class':
            self._parse_single_tok(toks, i, CppParseNodeType.CLASS_KEYWORD)
        elif tok == 'struct':
            self._parse_single_tok(toks, i, CppParseNodeType.STRUCT_KEYWORD)
        elif tok == 'public':
            self._parse_single_tok(toks, i, CppParseNodeType.SPECIFIER_KEYWORD)
        elif tok == 'private':
            self._parse_single_tok(toks, i, CppParseNodeType.SPECIFIER_KEYWORD)
        elif tok == 'protected':
            self._parse_single_tok(toks, i, CppParseNodeType.SPECIFIER_KEYWORD)
        elif tok == 'namespace':
            self._parse_single_tok(toks, i, CppParseNodeType.NAMESPACE_KEYWORD)
        elif tok == 'template':
            self._parse_single_tok(toks, i, CppParseNodeType.TEMPLATE_KEYWORD)
        elif tok == 'int':
            self._parse_single_tok(toks, i,
                                   CppParseNodeType.BUILTIN_TYPE_KEYWORD)
        elif tok == 'float':
            self._parse_single_tok(toks, i,
                                   CppParseNodeType.BUILTIN_TYPE_KEYWORD)
        elif tok == 'double':
            self._parse_single_tok(toks, i,
                                   CppParseNodeType.BUILTIN_TYPE_KEYWORD)
        elif tok == 'const':
            self._parse_single_tok(toks, i, CppParseNodeType.SPECIFIER_KEYWORD)
        elif tok == 'constexpr':
            self._parse_single_tok(toks, i, CppParseNodeType.SPECIFIER_KEYWORD)
        elif tok == 'static':
            self._parse_single_tok(toks, i, CppParseNodeType.SPECIFIER_KEYWORD)
        elif tok == 'inline':
            self._parse_single_tok(toks, i, CppParseNodeType.SPECIFIER_KEYWORD)
        return i + 1

    def _parse_single_tok(self, toks, i, node_type):
        self.cur_node.add_child(node_type)
        self.cur_node = self.cur_node.prior_child()
        self.cur_node.val = toks[i]
        self.cur_node = self.cur_node.parent
        return i + 1

    def get_root_node(self):
        return self.root_node