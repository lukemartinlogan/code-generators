from code_generators.cpp.cpp_parse import CppParse
from code_generators.cpp.cpp_parse_node import CppParseNodeType

def parse_strings():
    text = """
    "1234"
    '5'
    """

    parser = CppParse(text=text)
    parser.parse()
    assert(len(parser.get_root_node().children_) == 2)
    assert(parser.get_root_node().children_[0].node_type ==
           CppParseNodeType.STRING)
    assert(parser.get_root_node().children_[1].node_type ==
           CppParseNodeType.CHAR)
    assert(parser.get_root_node().children_[0].val == '1234')
    assert(parser.get_root_node().children_[1].val == '5')

def parse_comments():
    text = """
    /* hello1 */
    // hello2
    "123"
    """
    parser = CppParse(text=text)
    parser.parse()
    assert(parser.get_root_node().children_[0].node_type ==
           CppParseNodeType.COMMENT)
    assert(parser.get_root_node().children_[1].node_type ==
           CppParseNodeType.COMMENT)
    assert(parser.get_root_node().children_[2].node_type ==
           CppParseNodeType.STRING)
    assert(parser.get_root_node().children_[0].val == ' hello1 ')
    assert(parser.get_root_node().children_[1].val == ' hello2')
    assert(parser.get_root_node().children_[2].val == '123')
