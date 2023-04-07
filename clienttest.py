import socket
import json

def __send_servers_ip_port():
    request = {'function': 'Cadastro_Paciente', 'values': {'CPF': '10154389450', 'Nome': 'Francisco', 'Telefone': '81999932153', 'Email': 'luis.sda.3dqda@gmail.com', 'CEP': '51394123', 'Complem_Endereco': 'dasdadaNADa','Idade': 1, 'Genero': 'H', 'Nascimento': '15-03-2001'}}
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
    sock.settimeout(20)
    try:
        sock.connect(('127.0.0.1', 64979))
        print('Conectou')
        data = json.dumps(request, indent=2).encode('utf-8')
        sock.sendall(data)
        print('Enviou')
        data = sock.recv(1000)
        print('Recebeu -> ', data)
        data = json.loads(data.decode('utf-8'))
        print(data)
        sock.close()
    except Exception as e:
        print(f'[!] Error -> {e}')

__send_servers_ip_port()