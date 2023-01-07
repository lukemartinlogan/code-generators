"""
Tokenize C++ text
"""

import re
import sys, os


class CppLex:
    def __init__(self, text):
        self.text = text
        self.toks = None

    def lex(self):
        for path in self.paths:
            with open(path) as fp:
                text = fp.read()
                self._parse_text(text)
        if self.text is not None:
            self._parse_text(self.text)

    @staticmethod
    def _clean(toks):
        toks = [tok for tok in toks if tok is not None and len(tok) > 0]
        return toks

    def _split_cpp_toks(self, text):
        chars = ['\\\'', '\\\"', '\(', '\)', '<', '>', '\[', '\]', '\{', '\}',
                 '\+', '\-', '=', '\*', '/', '\|', '\*', '&', ',', '\:', ';',
                 '~', '!', '%', '#']
        chars = "".join(chars)
        chars = f"[{chars}]"
        toks = re.split(f"({chars}|\s+)", text)
        toks = CppLex._clean(toks)
        self.toks = toks
