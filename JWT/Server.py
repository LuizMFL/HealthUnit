import socket
from JWTPaciente import *
import json

class Server:
    def __init__(self) -> None:
        self.JWT = JWT()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
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
                if 'JWT' in data:
                    jwt_a = data['JWT']['value']
                    response = {'status': {'value': 401, 'message': 'token not exists'}, 'payload': ''}
                    if 'token' in jwt_a:
                        try:
                            response = self.JWT._validation_token(jwt['token'])
                        except Exception as e:
                            response = {'status': {'value': 401, 'message': str(e)}, 'payload': ''}
                    data['JWT']['response'] = response
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