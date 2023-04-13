import socket
import json
import re
from contextlib import contextmanager

#! Não vai dar pra fazer
class Gerenciador:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Insert_Especializacao': self.insert_especializacao,
            'Del_Especializacao': self.del_especializacao,
            'Insert_Doenca': self.insert_doenca,
            'Insert_Doenca_Remedio': self.insert_doenca_remedio,
            'Del_Doenca_Remedio': self.del_doenca_remedio,
            'Insert_Remedio_Estoque': self.insert_remedio_estoque,
            'Del_Remedio_Estoque': self.del_remedio_estoque,
            'Insert_Remedio': self.insert_remedio,
            'Del_Remedio': self.del_remedio,
            'Insert_Calendario': self.insert_calendario,
            'Del_Calendario': self.del_calendario,
            'Insert_Calendario_Especializacao_Medico': self.insert_calendario_especializacao_medico,
            'Del_Calendario_Especializacao_Medico': self.del_calendario_especializacao_medico,
            'Backup_DB': self.backup_db,
            'Get_Backups_DB': self.backup_db,
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


    def get_consultas_realizadas(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            cpf = value['CPF']
            response_get_rc =  self.get_profissional(cpf)
            if response_get_rc['Response'][0] == 200 and len(response_get_rc['Results']['Result']):
                id_rc = response_get_rc['Results']['Result'][0]['ID']
            
    def get_consultas_realizadas(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            cpf = value['CPF']
            response_get_rc =  self.get_profissional(cpf)
            if response_get_rc['Response'][0] == 200 and len(response_get_rc['Results']['Result']):
                id_rc = response_get_rc['Results']['Result'][0]['ID']
                get_con_rc = {'function': 'Select','table_name': 'consulta_profissional_reservada', 'where': self._normalize_type({'ID_Profissional': id_rc}, 'where')}
                response_get_con_rc = self.response_in_server(get_con_rc)
                response = {'Response': (200, 'Success!'), 'Results':{'Result': []}}
                for consulta_rc in response_get_con_rc['Results']['Result']:
                    id_con = consulta_rc['ID_Consulta']
                    get_con = {'function': 'Select','table_name': 'consulta', 'where': self._normalize_type({'ID': id_con}, 'where')}
                    response_get_con = self.response_in_server(get_con)
                    if response_get_con['Response'][0] == 200 and len(response_get_con['Results']['Result']):
                        response['Results']['Result'].append(response_get_con['Results']['Result'][0])
                    else:
                        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
                        break
        return response


if __name__ == '__main__':
    p = Gerenciador()
    a = p.cadastro_rc({'CPF': '10154389450', 'Nome': 'Francisco', 'Telefone': '81999932153', 'Email': 'luis.sda.3dqda@gmail.com', 'CEP': '51394123', 'Complem_Endereco': 'dasdadaNADa','Idade': 1, 'Genero': 'H', 'Nascimento': '15-03-2001'})
    print(a)
    b = p.get_profissional({'CPF':'10154389450'})
    print(b)
    c = p.get_consultas_realizadas({'CPF':'10154389450'})
    print(c)