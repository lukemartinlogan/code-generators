from code_generators.cpp.cpp_parse import CppParse
from code_generators.cpp.cpp_parse_node import CppParseNodeType

def parse_strings():
    text = """
    "1234"
    '5'
    """

    parser = CppParse(text=text)
    parser.parse()
    node = parser.get_root_node().get_children()
    assert(len(node) == 2)
    assert(node[0].is_one_of(CppParseNodeType.STRING))
    assert(node[1].is_one_of(CppParseNodeType.CHAR))
    assert(node[0].val == '1234')
    assert(node[1].val == '5')
    assert(text == parser.invert())

def parse_comments():
    text = """
    /* hello1 */
    // hello2
    "123"
    """
    parser = CppParse(text=text)
    parser.parse()
    nodes = parser.get_root_node().get_children()
    style_nodes = parser.get_style_nodes().get_children()
    assert(style_nodes[1].is_one_of(CppParseNodeType.ML_COMMENT))
    assert(style_nodes[3].is_one_of(CppParseNodeType.SL_COMMENT))
    assert(nodes[0].is_one_of(CppParseNodeType.STRING))
    assert(style_nodes[1].val == ' hello1 ')
    assert(style_nodes[3].val == ' hello2')
    assert(nodes[0].val == '123')
    assert(text == parser.invert())

def parse_macro():
    text = """
    #define HELLO hi
    
    int HELLO = 5;
    """

    parser = CppParse(text=text)
    parser.parse()
    parser.print()

def parse_macro_fun():
    text = """
    #define HELLO(TYPED_CLASS, TYPED_HEADER) \\
      TYPED_CLASS<TYPED_HEADER>

    int HELLO = 5;
    """

    parser = CppParse(text=text)
    parser.parse()
    parser.print()

def parse_function_proto():
    text = """
    void hello(int x1 = 25, int y2 = 100);
    """

    parser = CppParse(text=text)
    parser.parse()
    parser.print()
    nodes = parser.get_root_node().get_children()

    assert(nodes[0].is_one_of(CppParseNodeType.FUNCTION_DEF))
    assert(nodes[0][0].is_one_of(CppParseNodeType.TEXT))
    assert(nodes[0][1].is_one_of(CppParseNodeType.TEXT))
    assert(nodes[0][2].is_one_of(CppParseNodeType.PARAMS))

    assert(nodes[0][2][0].is_one_of(CppParseNodeType.PARAM))
    assert(nodes[0][2][0][0].is_one_of(CppParseNodeType.TYPE))
    assert(nodes[0][2][0][1].is_one_of(CppParseNodeType.TEXT))
    assert(nodes[0][2][0][2].is_one_of(CppParseNodeType.OP))
    assert(nodes[0][2][0][3].is_one_of(CppParseNodeType.TEXT))

    assert(nodes[0][2][1].is_one_of(CppParseNodeType.PARAM))
    assert(nodes[0][2][1][0].is_one_of(CppParseNodeType.TYPE))
    assert(nodes[0][2][1][1].is_one_of(CppParseNodeType.TEXT))
    assert(nodes[0][2][1][2].is_one_of(CppParseNodeType.OP))
    assert(nodes[0][2][1][3].is_one_of(CppParseNodeType.TEXT))

    assert(text == parser.invert())

def parse_function_body():
    text = """
    void hello(int x1 = 25, int y2 = 100) {
      int y = 0;
    }
    """

    parser = CppParse(text=text)
    parser.parse()
    parser.print()

    nodes = parser.get_root_node().get_children()
    assert (nodes[0].is_one_of(CppParseNodeType.FUNCTION_DEF))
    assert (nodes[0][0].is_one_of(CppParseNodeType.TEXT))
    assert (nodes[0][1].is_one_of(CppParseNodeType.TEXT))
    assert (nodes[0][2].is_one_of(CppParseNodeType.PARAMS))

    assert (nodes[0][2][0].is_one_of(CppParseNodeType.PARAM))
    assert (nodes[0][2][0][0].is_one_of(CppParseNodeType.TYPE))
    assert (nodes[0][2][0][1].is_one_of(CppParseNodeType.TEXT))
    assert (nodes[0][2][0][2].is_one_of(CppParseNodeType.OP))
    assert (nodes[0][2][0][3].is_one_of(CppParseNodeType.TEXT))

    assert (nodes[0][2][1].is_one_of(CppParseNodeType.PARAM))
    assert (nodes[0][2][1][0].is_one_of(CppParseNodeType.TYPE))
    assert (nodes[0][2][1][1].is_one_of(CppParseNodeType.TEXT))
    assert (nodes[0][2][1][2].is_one_of(CppParseNodeType.OP))
    assert (nodes[0][2][1][3].is_one_of(CppParseNodeType.TEXT))

    assert (nodes[0][2][2].is_one_of(CppParseNodeType.BRACES))
    assert (nodes[0][2][2][0].is_one_of(CppParseNodeType.TYPE))
    assert (nodes[0][2][2][1].is_one_of(CppParseNodeType.TEXT))
    assert (nodes[0][2][2][2].is_one_of(CppParseNodeType.OP))
    assert (nodes[0][2][2][3].is_one_of(CppParseNodeType.TEXT))

    assert (text == parser.invert())

def parse_lambda():
    text = """
    [] () {}
    [x,y] (int y, int z) { y + z; }
    """

    parser = CppParse(text=text)
    parser.parse()
    parser.print()
    assert(text == parser.invert())

def parse_class():
    text = """
    class y : public z {}
    """

    parser = CppParse(text=text)
    parser.parse()

    print(text)
    print()
    parser.print()

def parse_namespace():
    text = """
    namespace hello {

    class test {
     public:
      TEST void LocalHi(int x, int y);
      TEST void LocalLo(std::vector<int> y);

      #include "_test.h"
    };

    }  // namespace hello
    """

    parser = CppParse(text=text)
    parser.parse()

    print(text)
    print("---------------")
    print(parser.invert())
    assert (text == parser.invert())

def parse_template():
    text = """
    template<typename T>

    template<typename T, typename Y = X<T>,
             class Z = std::conditional<true, T, Y>>
    """

    parser = CppParse(text=text)
    parser.parse()
    parser.print()
    assert (text == parser.invert())

def parse_templated_class():
    text = """
    template<typename T>
    class y : public z {
     public:
     
      /** This is a docstring */
      template<typename T, typename Y>
      void x(25); 
    };
    """

    parser = CppParse(text=text)
    parser.parse()

    print(text)
    print()
    parser.print()

parse_strings()
#parse_comments()
#parse_macro()
#parse_macro_fun()
#parse_macro_fun()
#parse_function_proto()
#parse_function_body()
#parse_lambda()
#parse_class()
#parse_namespace()
#parse_template()
