import socket
import json
import re
from contextlib import contextmanager

class Medico:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Get_Especializacao': self.get_especializacoes,
            'Get_Doencas': self.get_doencas,
            'Get_Doenca_Remedio': self.get_doenca_remedio, #! Depende de Farmacia
            'Insert_Especializacao_Medico': self.insert_especializacao_medico,
            'Del_Especializacao_Medico': self.del_especializacao_medico,
            'Create_Receita': self.insert_receita,
            'Create_Receita_Remedio': self.insert_receita_remedio,
            'Del_Receita_Remedio': self.del_receita_remedio,
            'Reservar_Receita': self.reservar_receita, #? Envia um pedido de reservar para um servidor e nele terá o ID da receita (Toda complexidade de verificar estoque e atualizar ele deverá ser levada em consideração)
            'Get_Receitas': self.get_receitas, # ID_Paciente ou CPF #! Depende da Consulta
            'Get_Calendario_Medico': self.get_calendario_medico, #! Usar get_calendarios da Consulta
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
    
    def get_doenca_remedio(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        response_doenca = self.get_doencas(value)
        if response_doenca['Response'][0] == 200 and response_doenca['Results']['Response'] == 200:
            response = dict(response_doenca)
            response['Results']['Result'] = []
            for doenca in response_doenca['Results']['Result']:
                values = {'ID_Doenca': doenca['ID']}
                get_doe_rem = {'function': 'Select','table_name': 'doenca_remedio', 'where': self._normalize_type(values, 'where')}
                response_doe_remedio = self.response_in_server(get_doe_rem)
                if  response_doe_remedio['Response'][0] == 200 and response_doe_remedio['Results']['Response'] == 200:
                    for doe_remedio in response_doe_remedio['Results']['Result']:
                        values = {'ID_Remedio': doe_remedio['ID_Remedio']}
                        response_remedio = self.response_in_server(values, 'FC')
                        if response_remedio['Response'][0] == 200:
                            for key in doenca.keys():
                                doe_remedio[key] = doenca[key]
                            doe_remedio['Remedios'] = response_remedio['Results']['Result']
                            doe_remedio.pop('ID_Remedio')
                            doe_remedio.pop('ID_Doenca')
                            response['Results']['Result'].append(doe_remedio)
        return response
    def get_especializacoes(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'ID_Especializacao' in value.keys() and isinstance(value['ID_Especializacao'], int):
            values['ID'] = value['ID_Especializacao']
        elif 'Nome' in value.keys() and isinstance(value['Nome'], str):
            values['Nome'] = value['Nome']
        get_esp = {'function': 'Select','table_name': 'especializacao', 'where': self._normalize_type(values, 'where')}
        response_esp = self.response_in_server(get_esp)
        if response_esp['Response'][0] == 200 and response_esp['Results']['Response'][0] == 200:
            response = response_esp
        return response
    
    def get_doencas(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'ID_Doenca' in value.keys() and isinstance(value['ID_Doenca'], int):
            values['ID'] = value['ID_Doenca']
        elif 'Nome' in value.keys() and isinstance(value['Nome'], str):
            values['Nome'] = value['Nome']
        get_doe = {'function': 'Select','table_name': 'doenca', 'where': self._normalize_type(values, 'where')}
        response_doe = self.response_in_server(get_doe)
        if response_doe['Response'][0] == 200 and response_doe['Results']['Response'][0] == 200:
            response = response_doe
        return response
    
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