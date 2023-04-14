from flask import Flask, jsonify, request
import socket
import json
from contextlib import contextmanager

app = Flask(__name__)

servidores = {'Servidores': ('127.0.0.1', 64917), 'PR': ('127.0.0.1', 64918), 'PC': ('127.0.0.1', 64920), 
'MD': ('127.0.0.1', 64926), 'CS': ('127.0.0.1', 64924), 'FC': ('127.0.0.1', 64929), 'DB': ('127.0.0.1', 64940), 'RS': ('127.0.0.1', 64931)}

@app.route('/')
def index():
    return 'Hello, World!'
    
@app.route('/paciente/cadastro')
def cadastro_paciente():
    data = request.get_json(force=True)
    values = {'function': 'Cadastro_Paciente', 
    'values': 
    {'CPF': data['cpf'], 
    'Nome': data['nome'], 
    'Telefone': data['telefone'], 
    'Email': data['email'], 
    'CEP': data['cep'], 
    'Complem_Endereco': data['endereco'], 
    'Genero': data['genero'], 
    'Nascimento': data['nascimento']}}

    # Conexão com o servidor
    get_remedio = {'function': 'Get_Remedios', 'values': values}
    response_paciente = response_in_server(get_remedio, 'PC')
    print(response_paciente)
    status_code = response_paciente['Response']
    msg = response_paciente['Results']

    # Retornando 
    return jsonify(response_paciente)

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
    app.run()


""""
@app.route('/paciente/avaliacao/profissional/inserir')
def avaliacao_profissional_inserir():
    data = request.get_json(force=True)
    request_ = {'function': 'avaliacao_profissional', 
    'values': 
    {'ID_Profissional': data['id_profissional'], 
    'ID_Paciente': data['id_paciente'], 
    'Nota': data['nota'], 
    'Descricao': data['descricao'] }}

    # Conexão com o servidor
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
    sock.settimeout(20)
    sock.connect(('127.0.0.1', 44261))

    # Envio da solicitação
    sock.sendall(json.dumps(request_, indent=2).encode('utf-8'))

    # Obtenção da resposta
    response = sock.recv(1000)
    print(response)
    response = json.loads(response.decode('utf-8'))
    msg, status_code = response['Response']

    # Retornando 
    return jsonify({'msg': msg}), status_code

@app.route('/paciente/avaliacao/profissional/alterar')
def avaliacao_profissional_alterar():
    data = request.get_json(force=True)
    request_ = {'function': 'avaliacao_profissional', 
    'values': 
    {'ID_Profissional': data['id_profissional'], 
    'ID_Paciente': data['id_paciente'], 
    'Nota': data['nota'], 
    'Descricao': data['descricao'] }}

    # Conexão com o servidor
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
    sock.settimeout(20)
    sock.connect(('127.0.0.1', 44261))

    # Envio da solicitação
    sock.sendall(json.dumps(request_, indent=2).encode('utf-8'))

    # Obtenção da resposta
    response = sock.recv(1000)
    print(response)
    response = json.loads(response.decode('utf-8'))
    msg, status_code = response['Response']

    # Retornando 
    return jsonify({'msg': msg}), status_code

@app.route('/paciente/avaliacao/profissional/deletar')
def avaliacao_profissional_deletar():
    data = request.get_json(force=True)
    request_ = {'function': 'avaliacao_profissional', 
    'values': 
    {'ID_Profissional': data['id_profissional'], 
    'ID_Paciente': data['id_paciente'], 
    'Nota': data['nota'], 
    'Descricao': data['descricao'] }}

    # Conexão com o servidor
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
    sock.settimeout(20)
    sock.connect(('127.0.0.1', 44261))

    # Envio da solicitação
    sock.sendall(json.dumps(request_, indent=2).encode('utf-8'))

    # Obtenção da resposta
    response = sock.recv(1000)
    print(response)
    response = json.loads(response.decode('utf-8'))
    msg, status_code = response['Response']

    # Retornando 
    return jsonify({'msg': msg}), status_code
    """