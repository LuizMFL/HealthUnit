from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()

"""
from flask import Flask, jsonify, request
import socket
import json
from contextlib import contextmanager

app = Flask(__name__)

class api:
        
    def __init__(self):
        self.servers_ip_port = {}
        app.run()
    
    @app.route('/paciente/cadastro')
    def cadastro_paciente(self):
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
        response_paciente = ap.response_in_server(get_remedio, 'FC')
        status_code = response_paciente['Response']
        msg = response_paciente['Results']

        # Retornando 
        return jsonify({'msg': msg}), status_code

    def response_in_server(self, get:dict, server_name:str='DB'):
        data = json.dumps(get, indent=2).encode('utf-8')
        response = {'Response': (404, f'Error Connecting to {server_name} ')}
        if server_name in self.server.keys():
            try:
                with self.connection_to_server(server_name) as sock:
                    try:
                        sock.sendall(data)
                        data = sock.recv(1000)
                        data = json.loads(data.decode('utf-8'))
                        response['Results'] = data
                        response['Response'] = (200, 'Success')
                    except Exception as e:
                        response['Response'] = (401, str(e))
            except Exception as e:
                self.server.pop(server_name)
        return response

    @contextmanager
    def connection_to_server(self, server_name:str):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
            sock.settimeout(10)
            sock.connect(self.server[server_name])
            yield sock
            sock.close()
        except Exception as e:
            print(f'ERROR -> {e}')

ap=api()






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