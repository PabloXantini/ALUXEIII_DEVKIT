from utils.data import IDataEncoder
import json
class JSONEncoder(IDataEncoder):
    def __init__(self, format):
        super().__init__(format)
    def read(self, data):
        return json.loads(data)
    def write(self, data):
        return json.dumps(data).encode(self.format)