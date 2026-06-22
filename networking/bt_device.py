from __future__ import annotations

from utils.data import IDataEncoder
import socket

class BTDevice:
    def __init__(self, encoder, host, port=1):
        self.host = host
        self.port = port
        self.encoder:IDataEncoder = encoder
        self.s:socket.socket = None
    
    def setup(self) -> socket.socket:
        s = socket.socket(
            socket.AF_BLUETOOTH, 
            socket.SOCK_STREAM, 
            socket.BTPROTO_RFCOMM
        )
        return s

    def connect(self):
        self.s.connect((self.host, self.port))
    
    def close(self):
        self.s.close()

    def send(self, data:dict):
        data = self.encoder.write(data)
        self.socket.send(data)

    def receive(self) -> dict:
        data = self.s.recv(1024).decode(self.encoder.format)
        return self.encoder.read(data)
    