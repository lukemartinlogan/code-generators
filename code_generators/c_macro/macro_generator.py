import sys, os
from code_generators.cpp.cpp_parse import CppParse
from code_generators.cpp.cpp_parse_node import CppParseNodeType

class CppMacroGenerator:
    def generate(self, in_path, out_path,
                 macro_name, macro_vars, var_wraps, header_guard):
        # Parse the CPP file to get comments
        with open(in_path) as fp:
            text = fp.read()

        # Create the macro string
        if macro_vars is None:
            macro_vars_str = ""
        else:
            macro_vars_str = ','.join(macro_vars)
            macro_vars_str = f"({macro_vars_str})"

        # Wrap instances of macro var in the unmodified text
        if var_wraps is not None:
            for var_name, wrap in zip(macro_vars, var_wraps):
                if wrap is None:
                    continue
                text = text.replace(var_name, f"{wrap}({var_name})")
        lines = text.splitlines()

        # Create the hermes config string
        string_lines = []
        string_lines.append(f"#define {macro_name}{macro_vars_str}\\")
        for line in lines:
            string_lines.append(line + "\\")

        # Create the configuration
        config_lines = []
        config_lines.append(f"#ifndef {header_guard}")
        config_lines.append(f"#define {header_guard}")
        config_lines += string_lines
        config_lines.append(f"")
        config_lines.append(f"#endif  // {header_guard}")
        config_lines.append(f"")

        # Persist
        config = "\n".join(config_lines)
        with open(out_path, 'w') as fp:
            fp.write(config)

