import socket
from JWTFunctions import *
import json

class Server:
    def __init__(self) -> None:
        #self.DB = DataBase()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
        #self.socket.bind(('', 0))
        #print(self.socket.getsockname()[1])
        self.server_address = ('localhost', 5554)
        self.socket.bind(self.server_address)
        self.socket.listen(1)
        while True:
            print('[ ] Waiting for connection...')
            connection, client_address = self.socket.accept()
            print(f'[.] Connection Accept to client -> {client_address}')
            try:
                # Receive the data in small chunks and retransmit it
                data = connection.recv(1000)
                data = json.loads(data.decode('utf-8'))
                if data:
                    #data = self.DB.Select_function(data)
                    data = json.dumps(data, indent=2).encode('utf-8')
                    print('[+] Send Result to client...')
                    connection.sendall(data)
                else:
                    print('[-] Data None...')
                    break
            finally:
                # Clean up the connection
                print(f'[x] Connection Close with Client -> {client_address}!')
                connection.close()
                
if __name__ == '__main__':
    server = Server()