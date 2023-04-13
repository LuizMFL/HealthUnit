import socket
import json

def __send_servers_ip_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
    sock.settimeout(20)
    try:
        #request = {'function': 'Cadastro_Paciente', 'values': {'CPF': '15154389460', 'Nome': 'Francisco', 'Telefone': '81999932153', 'Email': 'luis.sda.3dqda@gmail.com', 'CEP': '51394123', 'Complem_Endereco': 'dasdadaNADa', 'Genero': 'H', 'Nascimento': '15/03/2001'}}
        request = {'function': 'Get_Paciente', 'values': {'CPF': '15154389460'}}
        #request = {'function': 'Update_Pe', 'values': {'CPF': '15154389460', 'Nome': 'George'}}
        #request = {'function': 'Del_Pessoa', 'values': {'CPF': '15154389460'}}
        sock.connect(('127.0.0.1', 57762))
        print('Conectou')
        data = json.dumps(request, indent=2).encode('utf-8')
        sock.sendall(data)
        print('Enviou')
        data = sock.recv(1000)
        data = json.loads(data.decode('utf-8'))
        print(data)
        sock.close()
    except Exception as e:
        print(f'[!] Error -> {e}')

__send_servers_ip_port()