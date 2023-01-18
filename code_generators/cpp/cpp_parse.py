from .cpp_parse0 import CppParse0
from .cpp_parse1 import CppParse1
from .cpp_parse2 import CppParse2
from .cpp_parse3 import CppParse3


class CppParse:
    def __init__(self, paths=None, text=None,
                 ignore_comments=False, ignore_spacing=False):
        self.paths = paths if paths is not None else []
        self.text = text
        self.parse_tree = None
        self.ignore_comments = ignore_comments
        self.ignore_spacing = ignore_spacing

    def parse(self):
        for path in self.paths:
            with open(path) as fp:
                text = fp.read()
                self._parse_text(text)
        if self.text is not None:
            self._parse_text(self.text)
        return self

    def _parse_text(self, text):
        phase0 = CppParse0(text).lex()
        phase1 = CppParse1(phase0, self.ignore_comments).parse()
        phase2 = CppParse2(phase1).parse()
        phase3 = CppParse3(phase2).parse()
        self.parse_tree = phase3

    def get_root_node(self):
        return self.parse_tree.get_root_node()

    def get_style_nodes(self):
        return self.parse_tree.get_style_nodes()

    def print(self):
        self.get_root_node().print()

    def invert(self):
        style_list = self.parse_tree.get_style_nodes().linearize()
        node_list = self.parse_tree.get_root_node().linearize()
        inverse_list = style_list + node_list
        inverse_list.sort(key=lambda x: x.start)
        text = "".join([x.join(ignore_hidden=False, inplace=False)
                        for x in inverse_list])
        return text
