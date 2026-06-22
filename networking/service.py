from abc import ABC, abstractmethod

class Service(ABC):
    def __init__(self, name:str):
        self.name = name
    @abstractmethod
    def process(self, data):
        pass