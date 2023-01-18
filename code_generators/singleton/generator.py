
"""
Create the .h and .cc files for defining Singletons
USAGE:
    cd hermes/code_generators/singleton
    python3 generate.py
"""

from enum import Enum


class SingletonType(Enum):
    GLOBAL_VAR = "GLOBAL"
    UNIQUE_PTR = "UNIQUE"
    SHARED_PTR = "SHARED"


class SingletonDefinition:
    def __init__(self, namespace, class_name, singleton_macro, include):
        self.macro_name = singleton_macro
        self.type_name = f"{self.macro_name}_T"
        if namespace is not None:
            self.class_name = f"{namespace}::{class_name}"
        else:
            self.class_name = class_name
        self.include = include


class SingletonGenerator:
    def __init__(self, singleton_include,
                 singleton_namespace,
                 type, singleton_name="Singleton"):
        """
        Creates the shared-object for a singleton class

        singleton_namespace: the namespace of the singleton
        singleton_include: location of singleton.hpp
        type: the type of singleton to generate
        singleton_name: the name of the singleton class
        """

        self.singleton_include = singleton_include
        self.guard_name = f"{singleton_namespace.replace('::', '_').upper()}"\
                          f"_{singleton_name.upper()}_H_"
        self.type = type
        if singleton_namespace is not None:
            self.singleton = f"{singleton_namespace}::{singleton_name}"
        else:
            self.singleton = f"{singleton_name}"
        self.defs = []

    def add(self, namespace, class_name, singleton_macro, include):
        """
        namespace: the namespace which the singleton class belongs to
        class_name: the name of the class to make a singleton
        singleton_macro: the macro to generate for the singleton
        include: the include of the class file
        """
        self.defs.append(SingletonDefinition(
            namespace, class_name, singleton_macro, include
        ))

    def generate(self, cc_file, h_file):
        self._generate_cc(cc_file)
        self._generate_h(h_file)

    def _generate_cc(self, path):
        lines = []
        lines.append(f"#include {self.singleton_include}")
        lines.append("")
        for defn in self.defs:
            lines.append(f"#include {defn.include}")
            if self.type == SingletonType.GLOBAL_VAR:
                lines.append(
                    "template<> " 
                    f"{defn.class_name} " 
                    f"{self.singleton}<{defn.class_name}>::obj_ = nullptr;")
            elif self.type == SingletonType.UNIQUE_PTR:
                lines.append(
                    "template<> "
                    f"std::unique_ptr<{defn.class_name}> "
                    f"{self.singleton}<{defn.class_name}>::obj_ = nullptr;")
            elif self.type == SingletonType.SHARED_PTR:
                lines.append(
                    "template<> " 
                    f"std::shared_ptr<{defn.class_name}> "
                    f"{self.singleton}<{defn.class_name}>::obj_ = nullptr;")
        self._save_lines(lines, path)

    def _generate_h(self, path):
        lines = []
        lines.append(f"#ifndef {self.guard_name}")
        lines.append(f"#define {self.guard_name}")
        lines.append("")
        lines.append(f"#include {self.singleton_include}")
        lines.append("")
        for defn in self.defs:
            lines.append(f"#define {defn.macro_name} " 
                         f"{self.singleton}<{defn.class_name}>::GetInstance()")
            lines.append(f"#define {defn.type_name} {defn.class_name}*")
            lines.append("")
        lines.append(f"#endif  // {self.guard_name}")
        self._save_lines(lines, path)

    def _save_lines(self, lines, path):
        text = "\n".join(lines) + "\n"
        if path is None:
            print(text)
            return
        with open(path, 'w') as fp:
            fp.write(text)