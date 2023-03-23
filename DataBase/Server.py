import socket
import sys
from DataBaseFunctions import *


class Server:
    def __init__(self) -> None:
        self.DB = DataBase()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 10000)
        self.socket.bind(self.server_address)
        while True:
            connection, client_address = self.socket.accept()
            try:
                # Receive the data in small chunks and retransmit it
                data = connection.recv(300)
                if data:
                    print >>sys.stderr, 'sending data back to the client'
                    connection.sendall(data)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
            finally:
                # Clean up the connection
                connection.close()
if __name__ == '__main__':
    my_dict = {'function': 'Insert','table_name': 'pessoa', 'where': [], 'values':[{'name':'CPF', 'value': '10854389458'}, {'name':'Nome', 'value':'Marcos'}, {'name':'Telefone', 'value':'81999496154'}, {'name':'Email', 'value': 'Luiz.sadadsadaakdajdadkasjdahdadkasskdad'}, {'name':'CEP', 'value':'51231333'}, {'name': 'Genero', 'value':'F'}, {'name':'Nascimento', 'value': date(2001, 4, 20)}, {'name': 'Complem_Endereco', 'value': 'Afonso'}, {'name': 'Idade', 'value': 15}]}
    size = sys.getsizeof(my_dict)
    print(my_dict)
    print(size)