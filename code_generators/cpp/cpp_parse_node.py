from enum import Enum


class CppParseNodeType(Enum):
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

    OP = "OP"
    ANGLE_BRACKET_LEFT = "ANGLE_BRACKET_LEFT"
    ANGLE_BRACKET_RIGHT = "ANGLE_BRACKET_RIGHT"
    COMMA = "COMMA"
    COLON = "COLON"
    SEMICOLON = "SEMICOLON"

    UNKOWN = "UNKOWN"


class CppParseNode:
    def __init__(self, node_type=CppParseNodeType.ROOT, val=None, parent=None):
        self.children_ = []
        self.parent = parent
        self.node_type = node_type
        self.val = val

    def add_child(self, node_type, val=None):
        self.children_.append(CppParseNode(node_type, val, self))

    def prior_child(self, count=1):
        return self.children_[-count]

    def join(self):
        return "".join([str(x) for x in self.children_])

    def copy_children(self):
        return self.children_.copy()

    def set_children(self, children):
        self.children_ = children

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

    def print(self, depth=0):
        for child in self.children_:
            print(f"{' ' * depth}{child.node_type}: {child.val}")
            child.print(depth + 2)