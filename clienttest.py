import socket
import json
from contextlib import contextmanager

servidores = {'Servidores': ('127.0.0.1', 52393), 'FC': ('127.0.0.1', 52395), 'MD': ('127.0.0.1', 52398), 'PC': ('127.0.0.1', 52397), 'PR': ('127.0.0.1', 52401), 'CS': ('127.0.0.1', 52403), 'RS': ('127.0.0.1', 52405), 'DB': ('127.0.0.1', 52409)}
def cadastro():
    request = {'function': 'Cadastro_Paciente', 'values': {'CPF': '030.560.000-02', 'Nome': 'Gloria', 'Telefone': '(81)99932-5436', 'Email': 'akdkakdakd@gmail.com', 'CEP': '40970-000', 'Complem_Endereco': 'Varzea', 'Genero': 'F', 'Nascimento': '10/04/1960'}}
    response = response_in_server(request, 'PC')
    print(response)

def get_paciente():
    request = {'function': 'Get_Paciente', 'values': {'CPF': '000.000.000-00', 'Nome': 'Robson', 'Telefone': '(81)99932-5436', 'Email': 'akdkakdakd@gmail.com', 'CEP': '40970-000', 'Complem_Endereco': 'Varzea', 'Genero': 'M', 'Nascimento': '10/04/1960'}}
    response = response_in_server(request, 'PC')
    print(response)
def response_in_server(get:dict, server_name:str='DB'):
    data = json.dumps(get, indent=2).encode('utf-8')
    response = {'Response': (404, f'Error Connecting to {server_name} ')}
    if server_name in servidores.keys():
        try:
            with connection_to_server(server_name) as sock:
                try:
                    sock.sendall(data)
                    data = sock.recv(1000)
                    data = json.loads(data.decode('utf-8'))
                    response['Results'] = data
                    response['Response'] = (200, 'Success')
                except Exception as e:
                    response['Response'] = (401, str(e))
        except Exception as e:
            servidores.pop(server_name)
    return response

@contextmanager
def connection_to_server(server_name:str):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
        sock.settimeout(10)
        sock.connect(servidores[server_name])
        yield sock
        sock.close()
    except Exception as e:
        print(f'ERROR -> {e}')

if __name__ == '__main__':
    cadastro()
    #get_paciente()