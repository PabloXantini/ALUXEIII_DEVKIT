from __future__ import annotations

from networking.bt_device import BTDevice
from utils.data import IDataEncoder
from utils.logging import logger
import socket

class BTClient(BTDevice):
    def __init__(self, encoder:IDataEncoder, host_server, port=1):
        super().__init__(encoder, port)
        self.host = host_server
    
    def request(self, header:str, content:dict):
        self.s = self.setup()
        self.s.settimeout(2.0)
        try:
            self.connect(self.host)
            request = {"header": header, "content": content}
            self.send(request)
            response = self.receive()
        except (OSError, socket.timeout) as e:
            logger.error(f"BlueTooth Client: Can't communicate with server: {e}")
            response = {
                "header": "Error Connection", 
                "status": "error", 
                "content": {}
            }
        finally:
            self.close()
        return response
