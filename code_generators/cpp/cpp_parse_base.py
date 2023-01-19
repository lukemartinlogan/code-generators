from .cpp_parse_node import CppParseNode, CppParseNodeType
from abc import ABC, abstractmethod


class CppParseBase:
    @abstractmethod
    def _parse(self, root_node, i, term):
        pass

    def _parse_grouping(self, root_node, i, node_type, term):
        """
        Group everything between starter and terminator recursively.

        :param i: the index of the left grouping (e..g, '(') in root_node
        :param term: the CppParseNodeType of the terminating node
        """
        i0 = i
        style_node = CppParseNode(CppParseNodeType.TEXT)
        group_node = CppParseNode(node_type)

        old_cur_node = self.cur_node
        self.cur_node = group_node
        # Add LEFT grouping to style node set
        style_node.add_child_node(root_node[i])
        # Parse everything up until the terminating character
        i = self._parse(root_node, i + 1, term=term)
        self.cur_node = old_cur_node

        # The last character must be the terminating character
        if not style_node[-1].is_one_of(term):
            self.add_error(root_node[i0], f"Unterminated {root_node[i0].val}")

        self.style_nodes.add_child_node(style_node)
        self.cur_node.add_child_node(group_node)
        return i + 1

    def _parse_args(self, root_node, i, node_type):
        """
        In a node which is known to be an argument list, this
        parses each parameter into its own node

        :param root_node: The node containing the parameters
        :param i: The offset within the node where parameter list starts

        """
        # Create param node
        i0 = i
        style_node = CppParseNode(CppParseNodeType.TEXT)
        params_node = CppParseNode(node_type=node_type,
                                    parent=root_node)
        param_node = CppParseNode(
            node_type=CppParseNodeType.PARAM,
            parent=params_node
        )
        parens_node = root_node[i]

        # Add each template argument
        i = 0
        while i < parens_node.size():
            node = parens_node[i]
            if node.node_type == CppParseNodeType.COMMA:
                style_node.add_child_node(node, hidden=True)
                params_node.add_child_node(param_node)
                param_node = CppParseNode(
                    node_type=CppParseNodeType.PARAM,
                    parent=params_node
                )
            else:
                param_node.add_child_node(node)
            i += 1
        params_node.add_child_node(param_node)
        root_node.replace_children(params_node, i0, i0)
        self.get_style_nodes().add_child_node(style_node)
        return i

    @abstractmethod
    def get_root_node(self):
        return self.parse_tree.get_root_node()

    @abstractmethod
    def get_style_nodes(self):
        return self.parse_tree.get_style_nodes()

    @abstractmethod
    def add_error(self, root_node, msg):
        pass

    @abstractmethod
    def get_errors(self):
        pass