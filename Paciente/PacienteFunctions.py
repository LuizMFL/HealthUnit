import socket
import json
import re
from contextlib import contextmanager

class Paciente:
    def __init__(self) -> None:
        self.server_DB = ('localhost', 5555)

    def get_paciente(self, cpf:str):
        response_pe = self.get_pessoa(cpf)
        if response_pe['Response'][0] == 200 and response_pe['Results']['Result']:
            get_pa = {'function': 'Select','table_name': 'paciente', 'where': [{'name': 'ID_Pessoa', 'operator': '=', 'value': response_pe['Results']['Result'][0]['ID']}]}
            response_pa = self.response_in_DB(get_pa)
            print('Paciente -> ', response_pa)
        print('Pessoa -> ', response_pe)
                
    def get_pessoa(self, cpf:str):
        cpf = re.sub('[^0-9]+', '', cpf)
        get_pe = {'function': 'Select','table_name': 'pessoa', 'where': [{'name': 'CPF', 'operator': '=', 'value': cpf}]}
        response = self.response_in_DB(get_pe)
        return response
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
    