# CPP

This sub-package is used to parse a C++ file for class definition, namespace
declarations, function prototypes, and templates. The parsing is based on a
simple, nearly-context-free analysis of the C++ files. It does not perform
any preprocessing or type checking (e.g., macros will not be descended into).

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