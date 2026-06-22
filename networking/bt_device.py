from __future__ import annotations

from utils.data import IDataEncoder
import socket

class BTDevice:
    def __init__(self, encoder, port=1):
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

    def connect(self, host):
        self.s.connect((host, self.port))
    
    def close(self):
        self.s.close()

    def send(self, data:dict):
        data = self.encoder.write(data)
        self.s.sendall(data)

    def receive(self) -> dict:
        data = self.s.recv(1024).decode(self.encoder.format)
        return self.encoder.read(data)
    