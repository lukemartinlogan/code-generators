from abc import ABC, abstractmethod


class Decorator(ABC):
    def __init__(self, name, state_requirements):
        self.name = name
        self.state_requirements = state_requirements

    @abstractmethod
    def generate(self, func_node, state):
        pass