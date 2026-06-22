from __future__ import annotations

import socket
import json
import threading
from networking.bt_device import BTDevice
from networking.service import Service
from utils.data import IDataEncoder
from utils.logging import logger

class BTServer(BTDevice):
    def __init__(self, encoder:IDataEncoder, host, port=10):
        super().__init__(encoder, host, port)
        self.running = False
        self.services:dict[str, Service] = {}
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        logger.msg(f"BlueTooth Server started on {self.address}")

    def stop(self):
        self.running = False
        self.thread.join()
        self.close()

    def register_service(self, name, service):
        self.services[name] = service

    def setup(self):
        self.s:socket.socket = super().setup()
        self.s.bind((self.host, self.port))
        self.s.listen(1)

    def _send(self, client:socket.socket, data):
        data = self.encoder.write(data)
        client.sendall(data)

    def run(self):
        self.setup()
        while self.running:
            client_s, _ = self.s.accept()
            raw_data = client_s.recv(1024).decode(self.encoder.format)
            if not raw_data:
                client_s.close()
                continue
            response = {
                "header": "unknown", 
                "status": "error", 
                "content": {}
            }
            try:
                request = json.loads(raw_data)
                header = request.get("header")
                content = request.get("content")
                if header in self.services:
                    response = self.services[header].process(content)
                
            except json.JSONDecodeError as e:
                logger.error(f"BlueTooth Server: JSON Decode Error: {e}")
                continue
            self._send(client_s, response)
            client_s.close()