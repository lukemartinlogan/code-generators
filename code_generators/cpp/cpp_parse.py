from .cpp_lex import CppLex
from .cpp_parse1 import CppParse1
from .cpp_parse2 import CppParse2
from .cpp_parse3 import CppParse3


class CppParse:
    def __init__(self, paths=None, text=None):
        self.paths = paths if paths is not None else []
        self.text = text
        self.parse_tree = None

    def parse(self):
        for path in self.paths:
            with open(path) as fp:
                text = fp.read()
                self._parse_text(text)
        if self.text is not None:
            self._parse_text(self.text)

    def _parse_text(self, text):
        lex = CppLex(text).lex()
        phase1 = CppParse1(lex).parse()
        phase2 = CppParse2(phase1).parse()
        phase3 = CppParse3(phase2).parse()
        self.parse_tree = phase1

    def get_root_node(self):
        return self.parse_tree.get_root_node()

    def print(self):
        self.get_root_node().print()
