import socket
import json
import re
from contextlib import contextmanager

class Medico:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Get_Calendario_Medico': self.get_calendario_medico,
            'Insert_Especializacao': self.insert_especializacao,
            'Del_Especializacao': self.del_especializacao,
            'Get_Doenca_Remedio': self.get_remedio,
            'Create_Receita': self.insert_receita,
            'Create_Receita_Remedio': self.insert_receita_remedio,
        }
        
    def Select_function(self, value:dict):
        try:
            self.server = value['Servidores']
            if value['function'] in self.functions.keys():
                value = self.functions[value['function']](value['values'])
            else:
                value['Response'] = (406, "Function not Exists")
                value['Result'] = ()
        except Exception:
            if isinstance(value, dict):
                value['Response'] = (406, 'Dict Format Error')
                value['Result'] = ()
            else:
                value = {'Response': (406, 'Data Type Error'), 'Result': ()}
        return value
    
    def _normalize_type(self, value:dict, option:str):
        value_aux = []
        #print('Valores recebidos -> ', value)
        for key in value.keys():
            x = value[key]
            if isinstance(x, str):
                correct = '[^a-zA-Z0-9-]'
                if key in ['CPF', 'Telefone', 'CEP']:
                    correct = '[^0-9]+'
                elif key == 'Nome':
                    correct = '[^a-zA-Z ]+'
                elif key == 'Nascimento':
                    correct =  '[^0-9|-]+'
                if option == 'values':
                    value_aux.append({'name': key, 'value': re.sub(correct, '', x)})
                elif option == 'where':
                    value_aux.append({'name': key, 'operator': '=', 'value': re.sub(correct, '', x)})
            else:
                value_aux.append({'name':key, 'operator': '=', 'value': x})
        #print('Valor final -> ', value_aux)
        return value_aux
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
            sock.connect(self.server[server_name])
            yield sock
        except Exception as e:
            print(f'ERROR -> {e}')
        finally:
            sock.close()
        yield

if __name__ == '__main__':
    p = Medico()
    a = p.cadastro_md({'CPF': '10154389450', 'Nome': 'Francisco', 'Telefone': '81999932153', 'Email': 'luis.sda.3dqda@gmail.com', 'CEP': '51394123', 'Complem_Endereco': 'dasdadaNADa','Idade': 1, 'Genero': 'H', 'Nascimento': '15-03-2001'})
    print(a)
    b = p.get_medico({'CPF':'10154389450'})
    print(b)
    c = p.get_consultas_realizadas({'CPF':'10154389450'})
    print(c)