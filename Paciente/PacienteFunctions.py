import socket
import json
import re
from contextlib import contextmanager

class Paciente:
    def __init__(self) -> None:
        self.server_DB = ('localhost', 5556)

    def get_paciente(self, cpf:str):
        response = {'Response': (406, 'Failed')}
        if len(cpf) == 11:
            response_pe = self.get_pessoa(cpf)
            response = dict(response_pe)
            response.pop('Results')
            if response_pe['Response'][0] == 200 and response_pe['Results']['Result']:
                get_pa = {'function': 'Select','table_name': 'paciente', 'where': [{'name': 'ID_Pessoa', 'operator': '=', 'value': response_pe['Results']['Result'][0]['ID']}]}
                response_pa = self.response_in_DB(get_pa)
                if response_pa['Response'][0] == 200 and response_pa['Results']['Result']:
                    response = response_pa
                    for key in response_pe['Results']['Result'][0].keys():
                        response['Results']['Result'][0][key] = response_pe['Results']['Result'][0][key]
            print('Paciente -> ', response)

    def get_pessoa(self, cpf:str):
        cpf = re.sub('[^0-9]+', '', cpf)
        get_pe = {'function': 'Select','table_name': 'pessoa', 'where': [{'name': 'CPF', 'operator': '=', 'value': cpf}]}
        response = self.response_in_DB(get_pe)
        return response
    def cadastro_pa(self, value:dict):
        pass
    def cadastro_pe(self, value:dict):
        set_pe = {'function': 'Insert', 'table_name': 'pessoa', 'values': [{'name':'CPF', 'value': re.sub('[^0-9]+', '',value['CPF'])}, {'name':'Nome', 'value':re.sub('[^a-zA-Z ]+', '',value['Nome'])}, {'name':'Telefone', 'value': re.sub('[^0-9]+', '',value['Telefone'])}, {'name':'Email', 'value': value['Email']}, {'name':'CEP', 'value': re.sub('[^0-9]+', '',value['CEP'])}, {'name': 'Genero', 'value': value['Genero']}, {'name':'Nascimento', 'value': str(value['Nascimento'])}, {'name': 'Complem_Endereco', 'value': value['Complem_Endereco']}, {'name': 'Idade', 'value': int(value['Idade'])}]}
        response_pa = self.response_in_DB(set_pe)
        print(response_pa)
    def response_in_DB(self, get:dict):
        data = json.dumps(get, indent=2).encode('utf-8')
        response = {}
        response['Response'] = get
        with self.connection_to_DB() as sock:
            try:
                sock.sendall(data)
                data = sock.recv(1000)
                data = json.loads(data.decode('utf-8'))
                response['Results'] = data
                response['Response'] = (200, 'Success')
            except Exception as e:
                response['Response'] = (401, str(e))
        return response

    @contextmanager
    def connection_to_DB(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 e TCP
            sock.connect(self.server_DB)
            yield sock
        except Exception as e:
            print(f'ERROR -> {e}')
        finally:
            sock.close()

if __name__ == '__main__':
    p = Paciente()
    p.get_paciente('108.543.894-58')
    
    print('___________________________')
    p.cadastro_pe({'CPF': '', 'Nome': 'Francisco', 'Telefone': '81999932153', 'Email': 'luis.sda.3dqda@gmail.com', 'CEP': '51394123', 'Complem_Endereco': 'dasdadaNADa','Idade': 0, 'Genero': 'H', 'Nascimento': '15-03-2001'})