import socket
import json
import sys
from datetime import date

def pedir(credentials):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
    server_address = ('localhost', 5554)
    sock.connect(server_address)
    try:
        my_dict = {'JWT': {'value': credentials}}
        print(my_dict)
        data = json.dumps(my_dict, indent=2).encode('utf-8')
        sock.sendall(data)
        data = sock.recv(1000)
        data = json.loads(data.decode('utf-8'))
        print(data)
    finally:
        print('Finallyss')
        sock.close()