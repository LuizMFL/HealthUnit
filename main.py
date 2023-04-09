from DataBase.Server import Server as ServerDB
from Paciente.Server import Server as ServerPaciente
from Farmacia.Server import Server as ServerFarmacia
from GerenciamentoUnidade.Server import Server as ServerGerenciador
from Medico.Server import Server as ServerMedico
from Recepcao.Server import Server as ServerRecepcionista
from Consulta.Server import Server as ServerConsulta
import socket
import json
from threading import Thread
import keyboard
import sys

class Servidores:
    def __init__(self) -> None:
        self.name_server = 'Servidores'
        self.servers_ip_port = {}
        self.__bind()
        self.__create_modules()
        Thread(target=self.server, args=(self,), daemon=True).start()
        self.exit()
        
    def exit(self):
        while True:  # making a loop
            try:  # used try so that if user pressed other than the given key error will not be shown
                if keyboard.is_pressed('q'):  # if key 'q' is pressed 
                    print('You Pressed A Key!')
                    sys.exit()
            except:
                break  # if user pressed a key other than the given key the loop will break

    def __create_modules(self):
        Thread(target=ServerDB, args=(dict(self.servers_ip_port),), daemon=True).start()
        Thread(target=ServerPaciente, args=(dict(self.servers_ip_port),), daemon=True).start()
        Thread(target=ServerFarmacia, args=(dict(self.servers_ip_port),), daemon=True).start()
        Thread(target=ServerGerenciador, args=(dict(self.servers_ip_port),), daemon=True).start()
        Thread(target=ServerMedico, args=(dict(self.servers_ip_port),), daemon=True).start()
        Thread(target=ServerRecepcionista, args=(dict(self.servers_ip_port),), daemon=True).start()
        Thread(target=ServerConsulta, args=(dict(self.servers_ip_port),), daemon=True).start()

    
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
        
    def __send_servers_ip_port(x, self):
        print(f'[=] {self.name_server}: Sending servers_ip_port...')
        request = {'function': 'AtualizarServers', 'Request': {'values': [dict(self.servers_ip_port)]}}
        for key in dict(self.servers_ip_port).keys():
            if not key == self.name_server:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
                sock.settimeout(20)
                try:
                    print(f'[ ] {self.name_server}: Connecting with Server {key} -> {self.servers_ip_port[key]}...')
                    sock.connect(self.servers_ip_port[key])
                    print(f'[.] {self.name_server}: Connection accepted to Server {key}')
                    print(f'[+] {self.name_server}: Sending servers_ip_port to Server {key}')
                    data = json.dumps(request, indent=2).encode('utf-8')
                    sock.sendall(data)
                    sock.close()
                except Exception as e:
                    print(f'[!] {self.name_server}: Error -> {e}')
                    self.servers_ip_port.pop(key)

    def server(x, self):
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
        self.servers_ip_port[value['name_server']] = tuple(value['values'][0])
        print(f'[%] {self.name_server}: Update server_ip_port {value["name_server"]} to {value["values"][0]}')
        Thread(target=self.__send_servers_ip_port, args=(self,), daemon=True).start()

if __name__ == '__main__':
    Servidores()