from utils.data import IData
import json
class JSONEncoder(IData):
    def __init__(self):
        pass
    def read(self, data):
        raw = json.loads(data)
    def write(self, data):
        return json.dumps(data).encode(self.format)