from networking.bt_server import BTServer
from networking.bt_client import BTClient
from utils.data import JSONEncoder
import dotenv
import os
from .api import ContextProvider

class Aluxe3NetBackend():
    def __init__(self, context):
        dotenv.load_dotenv()
        ADDR = os.getenv("SERVER_MAC_ADDR")
        PORT = int(os.getenv("BT_PORT"))
        self.server = BTServer(JSONEncoder(), ADDR, PORT)
        self.server.register_service("context", ContextProvider(context))
        self.client = BTClient(JSONEncoder(), ADDR, PORT)
    
    def start(self):
        self.server.start()
    
    def stop(self):
        self.server.stop()

        
    