# CPP

This package builds an "unmodified" parse tree of a C++ file. This parser is not
tied to any specific compiler implementation, such as gcc or clang. It is
intended to be used as a "code generator" phase, before type checking,
optimization, and such are performed.

## Usage

Parse some C++ text:
```python3
from code_generators.cpp.cpp_parse import cpp_parse

text = """
int hello(int x, int y, int z);
"""

parser = CppParse(paths=['hello.cc', 'hello.h'])
parser.parse()
parser.print()
parser.get_root_node()
```

Parse two C++ files:
```python
from code_generators.cpp.cpp_parse import CppParse

parser = CppParse(paths=['hello.cc', 'hello.h'])
parser.parse()
parser.print()
parser.get_root_node()
```
