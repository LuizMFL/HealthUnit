import socket
import json
import sys
from datetime import date

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
server_address = ('localhost', 10000)
sock.connect(server_address)
try:
    my_dict = {'function': 'Insert','table_name': 'pessoa', 'where': [], 'values':[{'name':'CPF', 'value': '10854389458'}, {'name':'Nome', 'value':'Marcos'}, {'name':'Telefone', 'value':'81999496154'}, {'name':'Email', 'value': 'Luiz.sadadsadaakdajdadkasjdahdadkasskdad'}, {'name':'CEP', 'value':'51231333'}, {'name': 'Genero', 'value':'F'}, {'name':'Nascimento', 'value': '15-03-2002'}, {'name': 'Complem_Endereco', 'value': 'Afonso'}, {'name': 'Idade', 'value': 15}]}
    size = sys.getsizeof(my_dict)
    print(my_dict)
    print(size)
    data = json.dumps(my_dict, indent=2).encode('utf-8')
    sock.sendall(data)
    data = sock.recv(1000)
    data = json.loads(data.decode('utf-8'))
    print(data)
finally:
    sock.close()