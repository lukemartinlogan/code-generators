from enum import Enum


class CppParseNodeType(Enum):
    # Phase 1 parsing
    ROOT = "ROOT"
    STRING = "STRING"
    CHAR = "CHAR"
    TEXT = "TEXT"
    SL_COMMENT = "SL_COMMENT"
    ML_COMMENT = "ML_COMMENT"
    BRACKETS = "BRACKETS"
    PARENS = "PARENS"
    BRACES = "BRACES"
    PREPROCESSOR = "PREPROCESSOR"

    # Phase 1 parsing
    CLASS_KEYWORD = 'CLASS_KEYWORD'
    STRUCT_KEYWORD = 'STRUCT_KEYWORD'
    NAMESPACE_KEYWORD = 'NAMESPACE_KEYWORD'
    TEMPLATE_KEYWORD = 'TEMPLATE_KEYWORD'
    TYPE = "TYPE"
    KEYWORD = "KEYWORD"

    # Phase 1 parsing
    OP = "OP"
    ANGLE_BRACKET_LEFT = "ANGLE_BRACKET_LEFT"
    ANGLE_BRACKET_RIGHT = "ANGLE_BRACKET_RIGHT"
    COMMA = "COMMA"
    COLON = "COLON"
    SEMICOLON = "SEMICOLON"

    # Phase 2 parsing
    FUNCTION = "FUNCTION"
    LAMBDA = "LAMBDA"
    CLASS_DEFN = "CLASS_DEFN"
    INHERITANCE = "INHERITANCE"
    NAMESPACE_DEFN = "NAMESPACE_DEFN"
    TEMPLATE_PARAMS = "TEMPLATE_PARAMS"
    TEMPLATE = "TEMPLATE"
    LAMBDA_CAPTURE_PARAMS = "LAMBDA_CAPTURE_PARAMS"
    PARAMS = "PARAMS"
    PARAM = "PARAM"
    BODY = "BODY"

    # Phase 3 parsing
    FUNCTION_PROTO = "FUNCTION_PROTO"
    FUNCTION_DEF = "FUNCTION_DEF"
    FUNCTION_CALL = "FUNCTION_CALL"

    # Unkown
    UNKOWN = "UNKOWN"


class CppParseNode:
    def __init__(self, node_type=CppParseNodeType.ROOT, val=None,
                 start=None, parent=None, hidden=False):
        self.children_ = []
        self.parent = parent
        self.node_type = node_type
        self.val = val
        self.start = start
        self.hidden = hidden

    def is_one_of(self, *types):
        for t in types:
            if self.node_type == t:
                return True
        return False

    def make_group_child(self, node_type, hidden=False):
        self.children_.append(CppParseNode(
            node_type, None, None, self, hidden))

    def make_tok_child(self, node_type, val,
                      start, hidden=False):
        self.children_.append(CppParseNode(
            node_type, val, start, self, hidden))

    def add_child_node(self, node, hidden=None):
        node = node.shallow_copy()
        if hidden is not None:
            node.hidden = hidden
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


    def next_child(self, i, count=1):
        i += count
        if i >= len(self.children_):
            return None
        return self.children_[i]

    def last_child(self, off=0):
        """
        Get the child at offset from the last child.

        :param off: The offset from the last child
        :return: The child node
        """
        i = len(self.children_) - 1
        i -= off
        while i > 0:
            node = self.children_[i]
            if not node.hidden:
                return node
            i -= 1
        return None

    def join(self, ignore_hidden=True, inplace=True, style_nodes=None):
        """
        Merge all child nodes as the value of this node

        :return: the merged string
        """
        if len(self.children_) == 0:
            val = self.val
            if val is None:
                val = ""
        elif ignore_hidden:
            val = "".join([x.join(ignore_hidden, inplace=False)
                           for x in self.children_ if not x.hidden])
        else:
            val = "".join([x.join(ignore_hidden, inplace=False)
                           for x in self.children_])
        if inplace:
            self.val = val
        return val

    def linearize(self, nodelist=None):
        """
        Convert the node into an array. Ignores nodes which do not represent
        some sort of text object.

        :return:
        """
        if nodelist is None:
            nodelist = []
        for node in self.children_:
            node.linearize(nodelist)
            if node.start is not None:
                nodelist.append(node)
        return nodelist

    def copy_children(self):
        return self.children_.copy()

    def set_children(self, children):
        self.children_ = children

    def size(self):
        return len(self.get_children())

    def get_children(self):
        return self.children_

    def shallow_copy(self):
        new_node = CppParseNode(self.node_type, self.val,
                                self.start, self.parent, self.hidden)
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