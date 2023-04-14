import socket
import json
import re
from contextlib import contextmanager

class Medico:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Get_Especializacao': self.get_especializacoes, # Opcional ID_Especializacao ou Nome
            #'Get_Doencas': self._get_doencas, # Opcional ID_Doenca ou Nome
            'Get_Doenca_Remedio': self.get_doenca_remedio, # Opcional ID_Doenca ou Nome #! Depende de Farmacia
            'Insert_Especializacao_Medico': self.insert_especializacao_medico, # ID_Especializacao e ID_Medico
            'Del_Especializacao_Medico': self.del_especializacao_medico, # ID_Especializacao e ID_Medico
            'Create_Receita': self.insert_receita, # ID_Paciente, ID_Consulta e Data_Validade
            'Create_Receita_Remedio': self.insert_receita_remedio, # ID_Receita, ID_Remedio e Quantidade
            'Get_Receita': self.get_receita, # ID_Consulta
            'Del_Receita_Remedio': self.del_receita_remedio, # ID_Receita e ID_Remedio, só deleta CASO ele não tenha sido retirado
            'Get_Especializacao_Medico': self.get_especializacao_medico #  Obrigatorio ID_Especializacao ou ID_Medico
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

    def get_especializacao_medico(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'ID_Especializacao' in value.keys() and isinstance(value['ID_Especializacao'], int):
            values['ID_Espeicalizacao'] = value['ID_Especializacao']
        if 'ID_Medico' in value.keys() and isinstance(value['ID_Medico'], int):
            values['ID_Medico'] = value['ID_Medico']
        if len(values.keys()):
            get_esp_med = {'function': 'Select','table_name': 'especializacao_medico', 'where': self._normalize_type(values, 'where')}
            response_esp_med = self.response_in_server(get_esp_med)
            if response_esp_med['Response'][0] == 200:
                response = dict(response_esp_med)
                response['Results']['Result'] = []
                for esp_med in response_esp_med['Results']['Result']:
                    values_m = {'ID': esp_med['ID_Medico']}
                    response_med = self._get_medico(values_m)
                    if response_med['Response'][0] == 200:
                        values_pr = {'ID_Profissional': response_med['Results']['Result'][0]['ID_Profissional']}
                        get_prof = {'function': 'Get_Profissional', 'values': values_pr}
                        response_prof = self.response_in_server(get_prof, 'PR')
                        if response_prof['Response'][0] == 200:
                            values_esp = {'ID_Especializacao': esp_med['ID_Especializacao']}
                            response_esp = self.get_especializacoes(values_esp)
                            if response_esp['Response'][0] == 200:
                                esp_med.pop('ID_Medico')
                                esp_med.pop('ID_Especializacao')
                                esp_med['Especializacao'] = response_esp['Results']['Result'][0]
                                esp_med['Medico'] = response_med['Results']['Result'][0]
                                response['Results']['Result'].append(esp_med)
        return response

    def _get_medico(self, value:dict):
        get_med = {'function': 'Select','table_name': 'medico', 'where': self._normalize_type(value, 'where')}
        response_receita_remedio = self.response_in_server(get_med)
        response = response_receita_remedio
        return response

    def del_receita_remedio(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Receita' in value.keys() and isinstance(value['ID_Receita'], int) and 'ID_Remedio' in value.keys() and isinstance(value['ID_Remedio'], int):
            values = {
                'ID_Receita': value['ID_Receita'],
                'ID_Remedio': value['ID_Remedio'],
                'Retirada': False
            }
            del_receita_remedio = {'function': 'Delete','table_name': 'receita_remedio', 'where': self._normalize_type(values, 'where')}
            response_receita_remedio = self.response_in_server(del_receita_remedio)
            if response_receita_remedio['Response'][0] == 200:
                response = response_receita_remedio
        return response

    def insert_receita(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int) and 'ID_Consulta' in value.keys() and isinstance(value['ID_Consulta'], int) and 'Data_Validade' in value.keys() and isinstance(value['Data_Validade'], str):
            values = {
                'ID_Paciente': value['ID_Paciente'],
                'ID_Consulta': value['ID_Consulta'],
                'Data_Validade': value['Data_Validade']
            }
            set_receita = {'function': 'Insert','table_name': 'receita', 'values': self._normalize_type(values, 'values')}
            response_receita = self.response_in_server(set_receita)
            if response_receita['Response'][0] == 200:
                response = response_receita
        return response
    
    # Retorna só IDs
    def get_receita(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Consulta' in value.keys() and isinstance(value['ID_Consulta'], int):
            values = {
                'ID_Consulta': value['ID_Consulta']
            }
            get_receita = {'function': 'Select', 'table_name': 'receita', 'where': self._normalize_type(values, 'where')}
            response_receita = self.response_in_server(get_receita)
            if response_receita['Response'][0] == 200:
                response = response_receita
        return response

    def insert_receita_remedio(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Receita' in value.keys() and isinstance(value['ID_Receita'], int) and 'ID_Remedio' in value.keys() and isinstance(value['ID_Remedio'], int) and 'Quantidade' in value.keys() and isinstance(value['Quantidade'], int) and value['Quantidade'] > 0:
            values = {
                'ID_Receita': value['ID_Receita'],
                'ID_Remedio': value['ID_Remedio'],
                'Quantidade': value['Quantidade'],
                'Retirada': False
            }
            set_receita_remedio = {'function': 'Insert','table_name': 'receita_remedio', 'values': self._normalize_type(values, 'values')}
            response_receita_remedio = self.response_in_server(set_receita_remedio)
            if response_receita_remedio['Response'][0] == 200:
                response = response_receita_remedio
        return response
    
    def insert_especializacao_medico(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Especializacao' in value.keys() and isinstance(value['ID_Especializacao'], int) and 'ID_Medico' in value.keys() and isinstance(value['ID_Medico'], int):
            values = {
                'ID_Especializacao': value['ID_Especializacao'],
                'ID_Medico': value['ID_Medico']
            }
            set_esp_med = {'function': 'Insert','table_name': 'especializacao_medico', 'values': self._normalize_type(values, 'values')}
            response_esp_med = self.response_in_server(set_esp_med)
            if response_esp_med['Response'][0] == 200:
                response = response_esp_med
        return response
    
    def del_especializacao_medico(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Especializacao' in value.keys() and isinstance(value['ID_Especializacao'], int) and 'ID_Medico' in value.keys() and isinstance(value['ID_Medico'], int):
            values = {
                'ID_Especializacao': value['ID_Especializacao'],
                'ID_Medico': value['ID_Medico']
            }
            set_esp_med = {'function': 'Delete','table_name': 'especializacao_medico', 'where': self._normalize_type(values, 'where')}
            response_esp_med = self.response_in_server(set_esp_med)
            if response_esp_med['Response'][0] == 200:
                response = response_esp_med
        return response
    
    def get_doenca_remedio(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        response_doenca = self._get_doencas(value)
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
                        get_remedio = {'function': 'Get_Remedios', 'values': values}
                        response_remedio = self.response_in_server(get_remedio, 'FC')
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
    
    def _get_doencas(self, value:dict):
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