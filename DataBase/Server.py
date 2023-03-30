import socket
import sys
from DataBaseFunctions import *
import json

class Server:
    def __init__(self) -> None:
        self.DB = DataBase()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
        #self.socket.bind(('', 0))
        #print(self.socket.getsockname()[1])
        self.server_address = ('localhost', 10000)
        self.socket.bind(self.server_address)
        self.socket.listen(1)
        while True:
            connection, client_address = self.socket.accept()
            try:
                # Receive the data in small chunks and retransmit it
                data = connection.recv(1000)
                x = data.decode('utf-8')
                print(x)
                data = json.loads(x)
                data
                if data:
                    data = self.DB.Select_function(data)
                    data = json.dumps(data, indent=2).encode('utf-8')
                    connection.sendall(data)
                else:
                    break
            finally:
                # Clean up the connection
                connection.close()
                
if __name__ == '__main__':
    server = Server()