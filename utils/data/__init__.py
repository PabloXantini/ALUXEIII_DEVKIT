from abc import ABC, abstractmethod
class IDataEncoder(ABC):
    def __init__(self, format):
        self.format = format
    @abstractmethod
    def read(self, data):
        pass
    @abstractmethod
    def write(self, data):
        pass
    