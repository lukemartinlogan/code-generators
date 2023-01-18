"""
Tokenize C++ text
"""

import re
import sys, os


class CppParse0:
    def __init__(self, text):
        self.text = text
        self.toks = None

    def lex(self):
        self._split_cpp_toks(self.text)
        return self

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
        toks = CppParse0._clean(toks)
        self.toks = toks
