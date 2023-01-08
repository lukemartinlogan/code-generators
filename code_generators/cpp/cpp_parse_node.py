from enum import Enum


class CppParseNodeType(Enum):
    # Phase 1 parsing
    ROOT = "ROOT"
    NAME = "NAME"
    STRING = "STRING"
    CHAR = "CHAR"
    TEXT = "TEXT"
    COMMENT = "COMMENT"
    BRACKETS = "BRACKETS"
    PARENS = "PARENS"
    ANGLE_BRACKETS = "ANGLE_BRACKETS"
    BRACES = "BRACES"
    FUNCTION = "FUNCTION"
    LAMBDA = "LAMBDA"
    PREPROCESSOR = "PREPROCESSOR"

    # Phase 1 parsing
    CLASS_KEYWORD = 'CLASS_KEYWORD'
    STRUCT_KEYWORD = 'STRUCT_KEYWORD'
    NAMESPACE_KEYWORD = 'NAMESPACE_KEYWORD'
    TEMPLATE_KEYWORD = 'TEMPLATE_KEYWORD'
    BUILTIN_TYPE_KEYWORD = "BUILTIN_TYPE_KEYWORD"
    SPECIFIER_KEYWORD = "SPECIFIER_KEYWORD"

    # Phase 1 parsing
    OP = "OP"
    ANGLE_BRACKET_LEFT = "ANGLE_BRACKET_LEFT"
    ANGLE_BRACKET_RIGHT = "ANGLE_BRACKET_RIGHT"
    COMMA = "COMMA"
    COLON = "COLON"
    SEMICOLON = "SEMICOLON"

    # Phase 2 parsing
    CLASS_DEFN = "CLASS_DEFN"
    INHERITANCE = "INHERITANCE"
    NAMESPACE_DEFN = "NAMESPACE_DEFN"
    TEMPLATE_PARAMS = "TEMPLATE_PARAMS"
    TEMPLATE = "TEMPLATE"
    LAMBDA_CAPTURE_PARAMS = "LAMBDA_CAPTURE_PARAMS"
    PARAMS = "PARAMS"
    PARAM = "PARAM"
    BODY = "BODY"

    # Unkown
    UNKOWN = "UNKOWN"


class CppParseNode:
    def __init__(self, node_type=CppParseNodeType.ROOT, val=None, parent=None):
        self.children_ = []
        self.parent = parent
        self.node_type = node_type
        self.val = val

    def add_child(self, node_type, val=None):
        self.children_.append(CppParseNode(node_type, val, self))

    def add_child_node(self, node):
        node = node.shallow_copy()
        node.parent = self
        self.children_.append(node)

    def add_child_nodes(self, root_node, start, end):
        """
        Add nodes from start to (including) end
        """
        for node in root_node.get_children()[start:end+1]:
            self.add_child_node(node)

    def replace_children(self, node, start, end):
        """
        Remove nodes from start to (including) end
        """
        self.children_ = self.children_[0:start] + [node] + \
                         self.children_[end+1:]

    def prior_child(self, count=1):
        return self.children_[-count]

    def join(self):
        self.val = "".join([str(x) for x in self.children_])
        self.children_ = []

    def copy_children(self):
        return self.children_.copy()

    def set_children(self, children):
        self.children_ = children

    def size(self):
        return len(self.children_)

    def get_children(self):
        return self.children_

    def shallow_copy(self):
        new_node = CppParseNode(self.node_type, self.val, self.parent)
        new_node.children_ = self.children_
        return new_node

    def __str__(self):
        if self.val is not None:
            return self.val
        else:
            return ''

    def __repr__(self):
        if self.val is not None:
            return self.val
        else:
            return ''

    def __getitem__(self, i):
        return self.children_[i]

    def print(self, depth=0):
        for child in self.children_:
            if child.val is not None:
                print(f"{' ' * depth}{child.node_type}: {child.val}")
            else:
                print(f"{' ' * depth}{child.node_type}:")
            child.print(depth + 2)