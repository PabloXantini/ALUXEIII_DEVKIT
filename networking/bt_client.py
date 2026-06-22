from __future__ import annotations

import socket
import json
from networking.bt_device import BTDevice
from utils.data import IDataEncoder

class BTClient(BTDevice):
    def __init__(self, encoder:IDataEncoder, host_server, port=1):
        super().__init__(encoder, host_server, port)
    
    def request(self, header:str, content:dict):
        self.setup()
        self.connect()
        request = {"header": header, "content": content}
        self.send(request)
        response = self.receive()
        self.close()
        return response
