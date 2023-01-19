from .cpp_parse0 import CppParse0
from .cpp_parse1 import CppParse1
from .cpp_parse2 import CppParse2
from .cpp_parse3 import CppParse3
from .cpp_parse4 import CppParse4
from .cpp_parse5 import CppParse5
from .cpp_parse_state import CppParseState


class CppParse:
    def __init__(self, paths=None, path=None, text=None, state=None,
                 do_preprocess=True):
        self.paths = paths if paths is not None else []
        self.path = path
        self.text = text
        self.parse_tree = None
        self.state = state
        self.do_preprocess = do_preprocess

    def parse(self):
        self._preprocess()
        #self._parse()

    def _preprocess(self):
        # Create the state used to track all parse trees
        if self.state is None:
            self.state = CppParseState()
        # Create parse trees for input paths
        if len(self.paths) > 1:
            for path in self.paths:
                CppParse(path=path, state=self.state)
        # Verify that this path has not already been parsed
        if self.path not in self.state.parse_trees:
            self.state.parse_trees[self.path] = self
        else:
            return self.state.parse_trees[self.path]
        # Create parse tree for this input path
        if self.path is not None:
            with open(self.path) as fp:
                self.text = fp.read()
        # Create parse tree for this path
        self._preprocess_text(self.text)
        return self

    def _preprocess_text(self, text):
        # Lex + Label
        self.phase0 = CppParse0(text).lex()
        self.phase1 = CppParse1(self.phase0).parse()
        # Parse Tree Modification
        self.phase2 = CppParse2(self.phase1).parse()
        self.phase3 = CppParse3(self.phase2).parse()
        self.parse_tree = self.phase3

    def _parse(self):
        # Parse tree modification
        self.phase2 = CppParse2(self.phase1)
        self.phase4 = CppParse4(self.phase3).parse()
        self.phase5 = CppParse5(self.phase4).parse()
        self.parse_tree = self.phase3

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
