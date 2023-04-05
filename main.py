from DataBase.Server import Server as ServerDB
#from Paciente.Server import Server as ServerPaciente
import socket
import json
import threading

class Servidores(threading.Thread):
    def __init__(self) -> None:
        self.name_server = 'Servidores'
        self.servers_ip_port = {}
        self.__bind()
        self.__create_modules()
        self.server()

    def __create_modules(self):
        thread.start_new_thread (ServerDB(self.servers_ip_port), self.servers_ip_port)
        #ServerPaciente(self.servers_ip_port)
        #! self.Medico = ServerMedico(self.servers_ip_port)
        #! self.Recepcao = ServerRecepcao(self.servers_ip_port)
        #! self.GerenciamentoUnidade = ServerGerenciamentoUnidade(self.servers_ip_port)
        #! self.Farmacia = ServerFarmacia(self.servers_ip_port)
        #! self.Gateway = ServerGateway(self.servers_ip_port)

    
    def reconnect(self):
        print(f'[º] {self.name_server}: Reconnecting Server...')
        self.__bind()
        self.__send_servers_ip_port()
        
    def __bind(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
        self.socket.bind(('127.0.0.1', 0))
        self.socket.listen(1)
        self.servers_ip_port[self.name_server] = self.socket.getsockname()
        print(f'[#] {self.name_server}: New ip_port -> {self.servers_ip_port[self.name_server]}')
        
    def __send_servers_ip_port(self):
        request = {'function': 'AtualizarServers', 'Request': {'values': [self.servers_ip_port]}}
        for key in self.servers_ip_port.keys():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
            try:
                print(f'[ ] {self.name_server}: Connecting with Server {key} -> {self.servers_ip_port[key]}...')
                sock.connect(self.servers_ip_port[key])
                print(f'[.] {self.name_server}: Connection accepted to Server {key}')
                print(f'[+] {self.name_server}: Sending servers_ip_port to Server {key}')
                data = json.dumps(request, indent=2).encode('utf-8')
                sock.sendall(data)
                sock.close()
            except Exception:
                print(f'[!] {self.name_server}: Error')
                self.servers_ip_port.pop(key)

    def server(self):
        while True:
            try:
                print(f'[ ] {self.name_server}: Waiting for connection...')
                connection, client_address = self.socket.accept()
                print(f'[.] {self.name_server}: Connection Accept to client -> {client_address}')
                # Receive the data in small chunks and retransmit it
                data = connection.recv(1000)
                data = json.loads(data.decode('utf-8'))
                if data and 'function' in data.keys() and data['function'] == 'AtualizarServers' and 'Request' in data.keys():
                    self.__new_server_ip_port(data['Request'])
                else:
                    print(f'[-] {self.name_server}: Data None...')
                # Clean up the connection
                print(f'[x] {self.name_server}: Connection Close with Client -> {client_address}!')
                connection.close()
            except Exception:
                print(f'[!] {self.name_server}: Error to Accept...')
                self.reconnect()
    
    def __new_server_ip_port(self, value:dict):
        self.servers_ip_port[value['name_server']] = value['values'][0]
        print(f'[%] {self.name_server}: Update server_ip_port {value["name_server"]} to {value["values"][0]}')
        self.__send_servers_ip_port()

if __name__ == '__main__':
    Servidores()