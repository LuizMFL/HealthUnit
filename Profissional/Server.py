import socket
from Profissional.ProfissionalFunctions import *
import json
from threading import Thread
from os import getppid, getpid
import sys
class Server:
    def __init__(self, servidores:dict) -> None:
        print(f'{__name__} -> ID: {getpid()} & Parent Process: {getppid()}')
        self.name_server = 'PR'
        self.servers_ip_port = dict(servidores)
        self.name_servidores = dict(servidores).popitem()[0]
        self.PR = Profissional()
        self.__bind()
        Thread(target=self.__send_ip_port_to_serverServidores, args=(self,), daemon=True).start()
        self.server()

    def server(self):
        while True:
            try:
                print(f'[ ] {self.name_server}: Waiting for connection...')
                connection, client_address = self.socket.accept()
                print(f'[.] {self.name_server}: Connection Accept to client -> {client_address}')
                # Receive the data in small chunks and retransmit it
                data = connection.recv(1000)
                data = json.loads(data.decode('utf-8'))
                if data and 'function' in data.keys():
                    if data['function'] == 'AtualizarServers' and 'Request' in data.keys():
                        self.__new_servers_ip_port(data['Request'])
                    elif data['function'] == 'DesligarServers':
                        self.__desligar_server()
                    else:
                        data['Servidores'] = dict(self.servers_ip_port)
                        data = self.PR.Select_function(data)
                        data = json.dumps(data, indent=2).encode('utf-8')
                        print(f'[+] {self.name_server}: Send Result to client...')
                        connection.sendall(data)
                else:
                    print(f'[-] {self.name_server}: Data None...')
                # Clean up the connection
                print(f'[x] {self.name_server}: Closed Connection with Client -> {client_address}!')
                connection.close()
            except Exception:
                print(f'[!] {self.name_server}: Error to Accept...')
                self.reconnect()

    def reconnect(self):
        print(f'[º] {self.name_server}: Reconnecting Server...')
        self.__bind()
        Thread(target=self.__send_ip_port_to_serverServidores, args=(self,), daemon=True).start()
        
    def __bind(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
        self.socket.bind(('127.0.0.1', 0))
        self.socket.listen(1)
        self.servers_ip_port[self.name_server] = self.socket.getsockname()
        print(f'[#] {self.name_server}: New ip_port -> {self.servers_ip_port[self.name_server]}')
        
    def __send_ip_port_to_serverServidores(x, self):
        request = {'function': 'AtualizarServers', 'Request': {'name_server': str(self.name_server), 'values': [tuple(self.servers_ip_port[self.name_server])]}}
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
            sock.settimeout(10)
            try:
                print(f'[ ] {self.name_server}: Connecting with Server {self.name_servidores} -> {self.servers_ip_port[self.name_servidores]}...')
                sock.connect(self.servers_ip_port[self.name_servidores])
                print(f'[.] {self.name_server}: Connection accepted to Server {self.name_servidores}')
                print(f'[+] {self.name_server}: Sending servers_ip_port to Server {self.name_servidores}')
                data = json.dumps(request, indent=2).encode('utf-8')
                sock.sendall(data)
                print(f'[x] {self.name_server}: Closing connection with Server {self.name_servidores}')
                sock.close()
                break
            except socket.timeout:
                print(f'[!] {self.name_server}: Time out Error')

    def __new_servers_ip_port(self, value:dict):
        self.servers_ip_port = {x:tuple(value['values'][0][x]) for x in value['values'][0].keys()}
        print(f'[%] {self.name_server}: Updated servers_ip_port')
    
    def __desligar_server(self):
        print(f'{self.name_server} -> shutting down server')
        sys.exit()
if __name__ == '__main__':
    server = Server()