from code_generators.singleton.generator import \
    SingletonGenerator, SingletonType


gen = SingletonGenerator(
    singleton_include="\"singleton.h\"",
    singleton_namespace="test",
    type=SingletonType.UNIQUE_PTR
)
gen.add(
    namespace="hermes",
    class_name="Hermes",
    singleton_macro="HERMES",
    include="<hermes.h>"
)
gen.generate("singleton.cc", "singleton.h")
