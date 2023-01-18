import sys, os
from code_generators.singleton.generator import SingletonGenerator
from code_generators.util.naming import to_camel_case, to_snake_case

class ApiClass:
    def __init__(self,
                 adapter_namespace, adapter_name,
                 singleton_include, singleton_namespace,
                 singleton_name, singleton_type,
                 apis, h_includes, cc_includes,
                 dir=None,
                 create_h=True, create_cc=False,
                 create_singleton=True):
        """
        adapter_namespace: the namespace to use for this adapter
        adapter_name: the name of the API intercepted (e.g., posix)
        singleton_include: the path to the singleton definition file
        singleton_namespace: the namespace of singleton
        singleton_name: the name of the singleton class (typically "Singleton")
        singleton_type: the type of singleton used (e.g., UNIQUE_PTR)
        apis: the list of APIs being intercepted
        h_includes: the set of files to include in the output h file
        cc_includes: the set of files to include in the output cc file
        create_h: whether or not to generate the h file
        create_cc: whether or not to generate the cc file
        create_singleton: whether or not to create the singleton files
        """

        self.apis = apis
        # Store params
        self.adapter_namespace = adapter_namespace
        self.adapter_name = adapter_name
        self.singleton_namespace = singleton_namespace
        self.singleton_name = singleton_name
        self.apis = apis
        self.h_includes = h_includes
        self.cc_includes = cc_includes
        self.dir = dir
        self.create_h = create_h
        self.create_cc = create_cc
        self.real_api_name = to_camel_case(f"{self.adapter_name}Api")
        self.guard = f"{adapter_namespace.upper()}_{adapter_name.upper()}_H_"
        self.cc_path = None
        self.h_path = None
        # Ensure that directory is set if create_cc or create_h is true
        if self.create_h or self.create_cc:
            if dir is None:
                dir = os.path.dirname(os.getcwd())
                dir = os.path.join(dir, self.adapter_namespace)
        # Create {adapter_name}_api.h
        self.h_name = f"{self.adapter_name}_api.h"
        if create_h:
            self.h_path = os.path.join(dir, self.h_name)
            print(f"Will create header {self.h_path}")
        # Create {adapter_name}_api.cc
        self.cc_name = f"{self.adapter_name}_api.cc"
        if create_cc:
            self.cc_path = os.path.join(dir, self.cc_name)
            print(f"Will create cpp file {self.cc_path}")
        # Create singleton.cc
        if create_singleton:
            self.singleton_cc = os.path.join(dir, 'singleton.cc')
            self.singleton_h = os.path.join(dir, 'singleton.h')
            self.singleton_macro = to_snake_case(self.real_api_name).upper()
            self.singleton = SingletonGenerator(
                singleton_include=singleton_include,
                singleton_namespace=singleton_namespace,
                type=singleton_type
            )
            self.singleton.add(
                namespace=adapter_namespace,
                class_name=self.real_api_name,
                singleton_macro=self.singleton_macro,
                include="hermes.h"  # TODO(llogan): fix
            )
            self.singleton.generate(self.singleton_cc,
                                    self.singleton_h)
            print(f"Will create singleton files")
        self.cc_lines = []
        self.h_lines = []
        self._create_h()
        self._create_cc()

    def _ns(self, ns, cls):
        if ns is None:
            return f"{cls}"
        else:
            return f"{ns}::{cls}"

    def _using_ns(self, ns, cls):
        return f"using {self._ns(ns, cls)};"

    def _create_cc(self):
        self.cc_lines.append("")

        # Includes
        self.cc_lines.append(f"bool {self.adapter_name}_intercepted = true;")
        self.cc_lines.append(f"#include \"{self.h_name}\"")
        self.cc_lines.append("")

        # Namespace simplification
        self.cc_lines.append(self._using_ns(self.adapter_namespace,
                                            self.adapter_name))
        self.cc_lines.append("")

        # Intercept function
        for api in self.apis:
            self.cc_lines.append(f"{api.api_str} {{")
            self.cc_lines.append(
                f"  auto real_api = {self.singleton_macro};")
            self.cc_lines.append(f"  REQUIRE_API({api.name});")
            self.cc_lines.append(
                f"  return real_api->{api.name}({api.pass_args()});")
            self.cc_lines.append(f"}}")
            self.cc_lines.append("")

        text = "\n".join(self.cc_lines)
        self.save(self.cc_path, text)

    def _create_h(self):
        self.h_lines.append("")
        self.h_lines.append(f"#ifndef {self.guard}")
        self.h_lines.append(f"#define {self.guard}")

        # Include files
        self.h_lines.append("#include <dlfcn.h>")
        self.h_lines.append("#include <iostream>")
        for include in self.h_includes:
            self.h_lines.append(f"#include {include}")
        self.h_lines.append("")

        # Require API macro
        self.require_api()
        self.h_lines.append("")

        # Create typedefs
        self.h_lines.append(f"extern \"C\" {{")
        for api in self.apis:
            self.add_typedef(api)
        self.h_lines.append(f"}}")
        self.h_lines.append(f"")

        # Create the class definition
        self.h_lines.append(f"namespace {self.adapter_namespace} {{")
        self.h_lines.append(f"")
        self.h_lines.append(f"/** Pointers to the real {self.adapter_name} */")
        self.h_lines.append(f"class {self.adapter_name} {{")

        # Create class function pointers
        self.h_lines.append(f" public:")
        for api in self.apis:
            self.add_intercept_api(api)
        self.h_lines.append(f"")

        # Create the symbol mapper
        self.h_lines.append(f"  API() {{")
        self.h_lines.append(f"    void *is_intercepted = (void*)dlsym(RTLD_DEFAULT, \"{self.adapter_name}_intercepted\");")
        for api in self.apis:
            self.init_api(api)
        self.h_lines.append(f"  }}")

        # End the class, namespace, and header guard
        self.h_lines.append(f"}};")
        self.h_lines.append(f"}}  // namespace {self.adapter_namespace}::{self.adapter_name}")
        self.h_lines.append("")
        self.h_lines.append("#undef REQUIRE_API")
        self.h_lines.append("")
        self.h_lines.append(f"#endif  // {self.guard}")
        self.h_lines.append("")

        text = "\n".join(self.h_lines)
        self.save(self.h_path, text)

    def require_api(self):
        self.h_lines.append(f"#define REQUIRE_API(api_name) \\")
        self.h_lines.append(f"  if (api_name == nullptr) {{ \\")
        self.h_lines.append(f"    LOG(FATAL) << \"Failed to map symbol: \" \\")
        self.h_lines.append(f"    #api_name << std::endl; \\")
        self.h_lines.append(f"    std::exit(1); \\")
        self.h_lines.append(f"   }}")

    def add_typedef(self, api):
        self.h_lines.append(f"typedef {api.ret} (*{api.type})({api.get_args()});")

    def add_intercept_api(self, api):
        self.h_lines.append(f"  /** {api.real_name} */")
        self.h_lines.append(f"  {api.type} {api.real_name} = nullptr;")

    def init_api(self, api):
        self.h_lines.append(f"    if (is_intercepted) {{")
        self.h_lines.append(f"      {api.real_name} = ({api.type})dlsym(RTLD_NEXT, \"{api.name}\");")
        self.h_lines.append(f"    }} else {{")
        self.h_lines.append(f"      {api.real_name} = ({api.type})dlsym(RTLD_DEFAULT, \"{api.name}\");")
        self.h_lines.append(f"    }}")
        self.h_lines.append(f"    REQUIRE_API({api.real_name})")

    def save(self, path, text):
        if path is None:
            print(text)
            return
        with open(path, "w") as fp:
            fp.write(text)