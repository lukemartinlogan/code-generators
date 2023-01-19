"""
An initial labeling of all tokens. No structural changes.
"""

import re
from .cpp_parse_node import CppParseNode, CppParseNodeType


class CppParse1:
    def __init__(self, lex=None):
        self.lex = lex
        self.root_node = None
        self.style_nodes = None
        self.cur_node = None

        #CPP operators
        self.operators = ['+', '-', '*', '/', '<', '>', '=', '?', '%', '@',
                          '&', '^', '|']

        #CPP keywords
        self.cpp0 = ['and', 'and_eq', 'asm', 'atomic_cancel', 'atomic_commit',
                     'atomic_noexcept', 'auto', 'bitand', 'bitor', 'bool',
                     'break', 'case', 'catch', 'char', 'class', 'compl',
                     'const', 'const_cast', 'continue', 'default', 'delete',
                     'do', 'double', 'dynamic_cast', 'else', 'enum', 'explicit',
                     'export', 'extern', 'false', 'float', 'for', 'friend',
                     'goto', 'if', 'inline', 'int', 'long', 'mutable',
                     'namespace', 'new', 'not', 'not_eq', 'operator', 'or',
                     'or_eq', 'private', 'protected', 'public', 'reflexpr',
                     'register', 'reinterpret_cast', 'return', 'short',
                     'signed', 'sizeof', 'static', 'static_cast', 'struct',
                     'switch', 'synchronized', 'template', 'this', 'throw',
                     'true', 'try', 'typedef', 'typeid', 'typename', 'union',
                     'unsigned', 'using', 'virtual', 'void', 'volatile',
                     'wchar_t', 'while', 'xor', 'xor_eq']
        self.cpp11 = self.cpp0 + ['alignas', 'alignof', 'char16_t', 'char32_t',
                                  'constexpr', 'decltype', 'noexcept',
                                  'nullptr', 'static_assert', 'thread_local']
        self.cpp17 = self.cpp11 + []
        self.cpp20 = self.cpp17 + ['char8_t', 'concept', 'consteval',
                                   'constinit', 'co_await', 'co_return',
                                   'co_yield', 'requires']
        self.cpp23 = self.cpp20 + []
        self.keywords = self.cpp23

        # CPP Type Keywords
        self.type_keywords0 = ['bool', 'char', 'double',  'float', 'int',
                               'void', 'wchar_t']
        self.type_keywords11 = self.type_keywords0 + ['char16_t', 'char32_t']
        self.type_keywords17 =  self.type_keywords11 + []
        self.type_keywords20 = self.type_keywords17 + ['char8_t']
        self.type_keywords23 = self.type_keywords20 + []
        self.type_keywords = self.type_keywords23

    def parse(self):
        self.root_node = CppParseNode()
        self.style_nodes = CppParseNode()
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
        i0 = i
        i += 2
        style_node = CppParseNode(CppParseNodeType.ML_COMMENT)
        style_node.make_tok_child(CppParseNodeType.TEXT,
                                  "/*", i0, hidden=True)
        while i < len(toks) - 1:
            tok1 = toks[i]
            tok2 = toks[i+1]
            if tok1 == '*' and tok2 == '/':
                style_node.make_tok_child(CppParseNodeType.TEXT,
                                          "*/", i, hidden=True)
                style_node.join()
                self.style_nodes.add_child_node(style_node)
                return i + 2
            style_node.make_tok_child(CppParseNodeType.TEXT, tok1, i)
            i += 1
        raise Exception("Couldn't find the end */ of the multi-line comment")

    def _parse_sl_comment(self, toks, i):
        """
        Parses a single-line comment (ends with \n)

        i: the index of the starting / of the //
        """
        i0 = i
        i += 2
        style_node = CppParseNode(CppParseNodeType.SL_COMMENT)
        style_node.make_tok_child(CppParseNodeType.TEXT,
                                  "//", i0, hidden=True)
        while i < len(toks):
            tok = toks[i]
            if '\n' in tok:
                style_node.make_tok_child(CppParseNodeType.TEXT, tok,
                                          i, hidden=True)
                break
            style_node.make_tok_child(CppParseNodeType.TEXT, tok, i)
            i += 1
        style_node.join()
        self.style_nodes.add_child_node(style_node)
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
        style_node = CppParseNode(CppParseNodeType.TEXT,
                                  toks[i], i, hidden=True)
        self.style_nodes.add_child_node(style_node)
        return i + 1

    def _parse_string(self, toks, i):
        """
        Parse to the end of a C++ string.

        :param i: the index of the \" token
        :return: the index of the token after the string ends
        """
        i0 = i
        i += 1
        style_node = CppParseNode(CppParseNodeType.TEXT, hidden=True)
        style_node.make_tok_child(CppParseNodeType.TEXT,
                                  toks[i0], i0, hidden=True)
        string_node = CppParseNode(CppParseNodeType.STRING)
        while i < len(toks):
            if self._is_string(toks, i):
                style_node.make_tok_child(CppParseNodeType.TEXT, toks[i],
                                          i, hidden=True)
                string_node.join()
                self.style_nodes.add_child_node(style_node)
                self.cur_node.add_child_node(string_node)
                return i + 1
            if self._is_multiline_sep(toks, i):
                style_node.make_tok_child(CppParseNodeType.TEXT, toks[i],
                                          i, hidden=True)
                i += 1
                continue
            string_node.make_tok_child(CppParseNodeType.TEXT, toks[i], i)
            i += 1
        raise Exception("Could not find end of string")

    def _parse_char(self, toks, i):
        """
        Parse to the end of a C++ char.

        :param i: the index of the \' token
        :return: the index of the token after the char ends
        """
        i0 = i
        i += 1
        style_node = CppParseNode(CppParseNodeType.TEXT, hidden=True)
        style_node.make_tok_child(CppParseNodeType.TEXT,
                                  toks[i0], i, hidden=True)
        char_node = CppParseNode(CppParseNodeType.CHAR)
        while i < len(toks):
            if self._is_char(toks, i):
                style_node.make_tok_child(CppParseNodeType.TEXT, toks[i],
                                          i, hidden=True)
                char_node.join()
                self.style_nodes.add_child_node(style_node)
                self.cur_node.add_child_node(char_node)
                return i + 1
            char_node.make_tok_child(CppParseNodeType.TEXT, toks[i], i)
            i += 1
        raise Exception("Could not find end of char")

    def _parse_preprocessor(self, toks, i):
        """
        Parse a C macro definition
        #[TEXT] [TEXT]\[TEXT]...

        :param toks:
        :param i: index of the '#' operator
        :return:
        """

        i0 = i
        i += 1

        style_node = CppParseNode(CppParseNodeType.TEXT)
        preprocess_node = CppParseNode(CppParseNodeType.PREPROCESSOR)
        preprocess_node.make_tok_child(CppParseNodeType.TEXT,
                                       f"#{toks[i]}", i0)
        i += 1
        while i < len(toks):
            if '\n' in toks[i]:
                if not self._is_multiline_sep(toks, i+1):
                    style_node.make_tok_child(CppParseNodeType.TEXT,
                                              toks[i], i, hidden=True)
                    preprocess_node.join()
                    self.style_nodes.add_child_node(preprocess_node)
                    self.cur_node.add_child_node(preprocess_node)
                    break
            preprocess_node.make_tok_child(CppParseNodeType.TEXT, toks[i], i)
            i += 1
        return i + 1

    def _parse_parens(self, toks, i):
        if toks[i] == '(':
            bracket_node = CppParseNode(CppParseNodeType.PAREN_LEFT,
                                        toks[i], i)
        else:
            bracket_node = CppParseNode(CppParseNodeType.PAREN_RIGHT,
                                        toks[i], i)
        self.cur_node.add_child_node(bracket_node)
        return i + 1

    def _parse_bracket(self, toks, i):
        if toks[i] == '[':
            bracket_node = CppParseNode(CppParseNodeType.BRACKET_LEFT,
                                        toks[i], i)
        else:
            bracket_node = CppParseNode(CppParseNodeType.BRACKET_RIGHT,
                                        toks[i], i)
        self.cur_node.add_child_node(bracket_node)
        return i + 1

    def _parse_brace(self, toks, i):
        if toks[i] == '{':
            bracket_node = CppParseNode(CppParseNodeType.BRACE_LEFT,
                                        toks[i], i)
        else:
            bracket_node = CppParseNode(CppParseNodeType.BRACE_RIGHT,
                                        toks[i], i)
        self.cur_node.add_child_node(bracket_node)
        return i + 1

    def _parse_angle_bracket(self, toks, i):
        if toks[i] == '<':
            bracket_node = CppParseNode(CppParseNodeType.ANGLE_BRACKET_LEFT,
                                        toks[i], i)
        else:
            bracket_node = CppParseNode(CppParseNodeType.ANGLE_BRACKET_RIGHT,
                                        toks[i], i)
        self.cur_node.add_child_node(bracket_node)
        return i + 1

    def _parse_comma(self, toks, i):
        return self._parse_single_tok(toks, i, CppParseNodeType.COMMA)

    def _parse_colon(self, toks, i):
        return self._parse_single_tok(toks, i, CppParseNodeType.COLON)

    def _parse_semicolon(self, toks, i):
        return self._parse_single_tok(toks, i, CppParseNodeType.SEMICOLON)

    def _is_op(self, toks, i):
        return toks[i] in self.operators

    def _parse_op(self, toks, i):
        return self._parse_single_tok(toks, i, CppParseNodeType.OP)

    def _parse_text(self, toks, i):
        if toks[i].isnumeric():
            return self._parse_single_tok(toks, i, CppParseNodeType.NUMBER)
        else:
            return self._parse_single_tok(toks, i, CppParseNodeType.TEXT)

    def _is_keyword(self, tok):
        return tok in self.keywords

    def _parse_keyword(self, toks, i):
        tok = toks[i]
        if tok == 'class':
            self._parse_single_tok(toks, i, CppParseNodeType.CLASS_KEYWORD)
        elif tok == 'struct':
            self._parse_single_tok(toks, i, CppParseNodeType.STRUCT_KEYWORD)
        elif tok == 'namespace':
            self._parse_single_tok(toks, i, CppParseNodeType.NAMESPACE_KEYWORD)
        elif tok == 'template':
            self._parse_single_tok(toks, i, CppParseNodeType.TEMPLATE_KEYWORD)
        elif tok == 'typedef':
            self._parse_single_tok(toks, i, CppParseNodeType.TEMPLATE_KEYWORD)
        elif tok == 'using':
            self._parse_single_tok(toks, i, CppParseNodeType.USING_KEYWORD)
        elif tok in self.type_keywords:
            self._parse_single_tok(toks, i,
                                   CppParseNodeType.TYPE)
        else:
            self._parse_single_tok(toks, i, CppParseNodeType.KEYWORD)
        return i + 1

    def _parse_single_tok(self, toks, i, node_type):
        tok_node = CppParseNode(node_type, toks[i], i)
        self.cur_node.add_child_node(tok_node)
        return i + 1

    def parse_multi_tok(self, toks, i, count, node_type):
        tok_node = CppParseNode(node_type)
        for k in range(count):
            tok_node.make_tok_child(CppParseNodeType.TEXT, toks[i+k], i+k)
        self.cur_node.add_child_node(tok_node)
        return i + count

    def get_root_node(self):
        return self.root_node

    def get_style_nodes(self):
        return self.style_nodes

    def add_error(self, root_node, msg):
        pass

    def get_errors(self):
        pass

    def _toks_match(self, toks, i, *vals):
        for val in vals:
            if i >= len(toks):
                return False
            if toks[i] != val:
                return False
            i += 1
        return True
