import sys, os
from code_generators.cpp.cpp_parse import CppParse
from code_generators.cpp.cpp_parse_node import CppParseNodeType

class CppMacroGenerator:
    def generate(self, in_path, out_path, macro_name, macro_vars, header_guard):
        # Parse the CPP file to get comments
        parser = CppParse(paths=[in_path], ignore_comments=True).parse()
        template_lines = parser.invert().splitlines()

        # Create the macro string
        if macro_vars is None:
            macro_vars_str = ""
        else:
            macro_vars_str = ','.join(macro_vars)
            macro_vars_str = f"({macro_vars_str})"

        # Create the hermes config string
        string_lines = []
        string_lines.append(f"#define {macro_name}{macro_vars_str}\\")
        for line in template_lines:
            string_lines.append(line + "\\")
        string_lines[-1] = string_lines[-1] + ';'

        # Create the configuration
        config_lines = []
        config_lines.append(f"#ifndef {header_guard}")
        config_lines.append(f"#define {header_guard}")
        config_lines += string_lines
        config_lines.append(f"#endif  // {header_guard}")

        # Persist
        config = "\n".join(config_lines)
        with open(out_path, 'w') as fp:
            fp.write(config)

