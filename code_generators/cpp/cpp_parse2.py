"""
Identifies:
1. Functions / lambdas defintions (untemplated)
2. Template argument lists
3. Class/struct definitions
4. Namespace declarations

This parsing is not perfect, as we do not go into the complexity of type
checking and preprocessing. This makes some assumptions about the style of the
C++ code.
"""

import re
from .cpp_parse_node import CppParseNode, CppParseNodeType


class CppParse2:
    def __init__(self, parse_tree=None):
        self.parse_tree = parse_tree

    def parse(self):
        self._reparse(self.parse_tree.get_root_node())
        return self

    def _reparse(self, root_node):
        i = 0
        while i < root_node.size():
            node = root_node[i]
            if self._check_if_function(root_node, i):
                i = self._parse_function(root_node, i)
                continue
            elif node.node_type == CppParseNodeType.BRACKETS:
                ret = self._check_if_lambda(root_node, i)
                if ret > 0:
                    i = ret
                    continue
            elif node.node_type == CppParseNodeType.ANGLE_BRACKET_LEFT:
                ret = self._check_if_template_params(root_node, i)
                if ret > 0:
                    i = ret
                    continue
            elif node.node_type == CppParseNodeType.CLASS_KEYWORD:
                ret = self._parse_class_defn(root_node, i)
                if ret > 0:
                    i = ret
                    continue
            elif node.node_type == CppParseNodeType.STRUCT_KEYWORD:
                ret = self._parse_class_defn(root_node, i)
                if ret > 0:
                    i = ret
                    continue
            elif node.node_type == CppParseNodeType.NAMESPACE_KEYWORD:
                ret = self._parse_namespace_defn(root_node, i)
                if ret > 0:
                    i = ret
                    continue
            i += 1

    def _parse_class_defn(self, root_node, i):
        """
        Converts:
        [class/struct] [TEXT] [BRACES]
        [class/struct] [TEXT] [COLON] [ANYTHING] [BRACES]
        Into: [CLASS_DEFN]

        i: Pointer to the class or struct keyword
        """

        # First word must be either class or struct
        i0 = i
        node = root_node[i]
        if node.node_type == CppParseNodeType.CLASS_KEYWORD:
            pass
        elif node.node_type == CppParseNodeType.STRUCT_KEYWORD:
            pass
        else:
            return -1
        i += 1

        # Next word must be [TEXT]
        node = root_node[i]
        if node.node_type != CppParseNodeType.TEXT:
            return -1
        i += 1

        # Next may be "colon" for inheritance
        node = root_node[i]
        if node.node_type == CppParseNodeType.COLON:
            ret = self._parse_inherit(root_node, i)
            if ret < 0:
                return -1
            i = ret

        # Last may be "body"
        node = root_node[i]
        if node.node_type == CppParseNodeType.BRACES:
            node.node_type = CppParseNodeType.BODY
            self._reparse(node)
            i += 1

        # Update the root node
        class_def_node = CppParseNode(node_type=CppParseNodeType.CLASS_DEFN,
                                      parent=root_node)
        class_def_node.add_child_nodes(root_node, i0 + 1, i - 1)
        root_node.replace_children(class_def_node, i0, i - 1)
        return i0 + 1

    def _parse_inherit(self, root_node, i):
        """
        Parses the inheritance part of a C++ class definition

        Converts:
        [COLON] [!BRACES]
        Into: [INHERIT]

        i: The index of [COLON] in root_node
        """

        i0 = i
        while i < root_node.size():
            node = root_node[i]
            if node.node_type == CppParseNodeType.BRACES:
                break
            i += 1
        inherit_node = CppParseNode(node_type=CppParseNodeType.INHERITANCE,
                                     parent=root_node)
        inherit_node.add_child_nodes(root_node, i0 + 1, i - 1)
        root_node.replace_children(inherit_node, i0, i - 1)
        return i0 + 1

    def _parse_namespace_defn(self, root_node, i):
        """
        Converts:
        [namespace] [NAMESPACED_TEXT] [BRACES]
        Into: [NAMESPACE_DEFN]
        """
        i0 = i

        # First node must be "namespace"
        node = root_node[i]
        if node.node_type != CppParseNodeType.NAMESPACE_KEYWORD:
            return -1
        i += 1

        # Next node is the namespace text
        ret = self._parse_namespace_text(root_node, i)
        if ret < 0:
            return -1
        i = ret
        if i >= root_node.size():
            return -1

        # Next node is possilby the namespace body
        node = root_node[i]
        if node.node_type != CppParseNodeType.BRACES:
            return -1
        node.node_type = CppParseNodeType.BODY
        self._reparse(node)
        i += 1

        # Update the root node
        ns_def_node = CppParseNode(node_type=CppParseNodeType.NAMESPACE_DEFN,
                                   parent=root_node)
        ns_def_node.add_child_nodes(root_node, i0 + 1, i - 1)
        root_node.replace_children(ns_def_node, i0, i - 1)
        return i0 + 1

    def _parse_namespace_text(self, root_node, i):
        """
        Converts:
        ([TEXT] [COLON] [COLON])+
        Into: [TEXT]
        """
        i0 = i
        ns_node = CppParseNode(node_type=CppParseNodeType.TEXT,
                               parent=root_node)
        while i < root_node.size():
            node = root_node[i]
            next_node = None
            if i + 1 < root_node.size():
                next_node = root_node[i+1]
            if node.node_type == CppParseNodeType.TEXT:
                ns_node.add_child_node(node)
            elif node.node_type == CppParseNodeType.COLON and \
                    next_node is not None and \
                    next_node.node_type == CppParseNodeType.COLON:
                ns_node.add_child_node(node)
                ns_node.add_child_node(next_node)
                i += 2
                continue
            else:
                break
            i += 1
        ns_node.join()
        root_node.replace_children(ns_node, i0, i)
        return i0 + 1

    def _parse_function(self, root_node, i):
        """
        Converts the pattern:
        [TEXT]+ [PARENS] OR
        [COMMENT] [TEXT]+ [PARENS]

        into [FUNCTION]

        root_node: the node containing [TEXT]+ [PARENS]
        i: index of parens in the root_node
        """

        text_count = self._text_iter_reverse(root_node, i - 1)
        i0 = i - text_count
        if i0 > 0 and root_node[i0 - 1].node_type == CppParseNodeType.COMMENT:
            i0 -= 1
        i = self._parse_args(root_node, i, CppParseNodeType.PARAMS)
        function_node = CppParseNode(node_type=CppParseNodeType.FUNCTION,
                                     parent=root_node)
        function_node.add_child_nodes(root_node, i0, i - 1)
        root_node.replace_children(function_node, i0, i - 1)
        return i0 + 1

    def _check_if_lambda(self, root_node, i):
        """
        Converts the pattern:
        [BRACKETS] [TEMPLATE_ARGS].(0,1) [TEXT]* [PARENS] [BRACES]
        into [LAMBDA]
        """

        i0 = i

        # First node must be brackets
        node = root_node[i]
        if node.node_type != CppParseNodeType.BRACKETS:
            return -1
        ret = self._parse_args(root_node, i,
                               CppParseNodeType.LAMBDA_CAPTURE_PARAMS)
        if ret < 0:
            return -1
        i = ret

        # Check if template params
        ret = self._check_if_template_params(root_node, i)
        if ret > 0:
            i = ret

        # Text is optional
        num_text = self._text_iter(root_node, i)
        i += num_text

        # Parenthesis required
        node = root_node[i]
        if node.node_type == CppParseNodeType.PARENS:
            i = self._parse_args(root_node, i, CppParseNodeType.PARAMS)
        else:
            return -1

        # Braces optional
        if i < root_node.size():
            node = root_node[i]
            if node.node_type == CppParseNodeType.BRACES:
                node.node_type = CppParseNodeType.BODY
                i += 1

        # Create new lambda supernode
        lambda_node = CppParseNode(node_type=CppParseNodeType.LAMBDA,
                                   parent=root_node)
        lambda_node.add_child_nodes(root_node, i0, i - 1)
        root_node.replace_children(lambda_node, i0, i - 1)
        return i0 + 1

    def _check_if_template_params(self, root_node, i):
        """
        Converts the pattern:
        [ANGLE_BRACKET_LEFT] anything but semicolon [ANGLE_BRACKET_RIGHT]
        into: [TEMPLATE_ARGS]

        <x, y, z>
        <typename X>
        <typename X, typename Y = X<T>>

        This is not entirely correct, as it's possible to have:
        int y = 25 < 16 > 32, which is just arithmetic;
        """

        i0 = i

        # Check if first node is "<"
        node = root_node[i]
        if node.node_type != CppParseNodeType.ANGLE_BRACKET_LEFT:
            return -1
        i += 1

        # Create template param node
        tparams_node = CppParseNode(node_type=CppParseNodeType.TEMPLATE_PARAMS,
                                parent=root_node)
        param_node = CppParseNode(
            node_type=CppParseNodeType.PARAM,
            parent=tparams_node
        )

        # Add each template argument
        while i < root_node.size():
            node = root_node[i]
            if node.node_type == CppParseNodeType.ANGLE_BRACKET_RIGHT:
                tparams_node.add_child_node(param_node)
                root_node.replace_children(tparams_node, i0, i)
                return i0 + 1
            elif node.node_type == CppParseNodeType.COMMA:
                tparams_node.add_child_node(param_node)
                param_node = CppParseNode(
                    node_type=CppParseNodeType.PARAM,
                    parent=tparams_node
                )
            elif node.node_type == CppParseNodeType.ANGLE_BRACKET_LEFT:
                ret = self._check_if_template_params(root_node, i)
                if ret > 0:
                    i = ret
            elif node.node_type == CppParseNodeType.SEMICOLON:
                return 0
            else:
                param_node.add_child_node(node)
            i += 1
        return 0

    def _check_if_function(self, root_node, i):
        """
        Check if the pattern matches:
        [TEXT] [PARENS]

        i: the location of [PARENS] in root_node
        """
        if i == 0:
            return False
        node = root_node[i]
        prior_node = root_node[i - 1]
        if node.node_type != CppParseNodeType.PARENS:
            return False
        return prior_node.node_type == CppParseNodeType.TEXT

    def _parse_args(self, root_node, i, node_type):
        """
        In a node which is known to be an argument list,
        this parses the type, name, and value of the argument.
        """
        # Create param node
        i0 = i
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
                params_node.add_child_node(param_node)
                param_node = CppParseNode(
                    node_type=CppParseNodeType.PARAM,
                    parent=params_node
                )
            elif node.node_type == CppParseNodeType.SEMICOLON:
                return -1
            else:
                param_node.add_child_node(node)
            i += 1
        params_node.add_child_node(param_node)
        root_node.replace_children(params_node, i0, i0)
        return i0 + 1

    def _text_iter(self, root_node, i):
        count = 0
        while i < root_node.size():
            node = root_node[i]
            if node.node_type != CppParseNodeType.TEXT:
                break
            count += 1
            i += 1
        return count

    def _text_iter_reverse(self, root_node, i):
        count = 0
        while i >= 0:
            node = root_node[i]
            if node.node_type != CppParseNodeType.TEXT:
                break
            count += 1
            i -= 1
        return count

    def get_root_node(self):
        return self.parse_tree.get_root_node()
