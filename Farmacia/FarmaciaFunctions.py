import socket
import json
import re
from datetime import datetime
from contextlib import contextmanager

class Farmacia:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Get_Remedios': self.get_remedios, # Opcional ID_Remedio e Nome
            'Get_Estoque': self.get_estoque, # Opcional ID_Remedio
            'Entregar_Medicamento': self.entregar_medicamento,
            'Get_Receita_Remedio': self.get_receita_remedio, # ID_Receita entrega tudo da receita_remedio (usa get_remedios para completar) e entrega mo ID_Receita
            'Update_Remedio_Estoque': self.update_remedio_estoque, 
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

    #validar com Luiz
    def get_remedios(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'ID_Remedio' in value.keys() and isinstance(value['ID_Remedio'], int):
            values['ID'] = value['ID_Remedio']
        elif 'Nome' in value.keys() and isinstance(value['Nome'], str):
            values['Nome'] = value['Nome']
        get_remedio = {'function': 'Select','table_name': 'remedio', 'where': self._normalize_type(values, 'where')}
        response_remedio = self.response_in_server(get_remedio)
        if response_remedio['Response'][0] == 200 and response_remedio['Results']['Response'][0] == 200:
            response = response_remedio
        return response

    # Validar com Luiz
    def get_estoque(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'ID_Estoque' in value.keys() and isinstance(value['ID_Estoque'], int):
            values = {
                'ID': value['ID_Estoque']
            }
        elif 'ID_Remedio' in value.keys() and isinstance(value['ID_Remedio'], int):
            values['ID_Remedio'] = value['ID_Remedio']
        get_estoque = {'function': 'Select', 'table_name': 'estoque', 'where': self._normalize_type(values, 'where')}
        response_estoque = self.response_in_server(get_estoque)
        if response_estoque['Response'][0] == 200:
            response = dict(response_estoque)
            response['Results']['Result'] = []
            for estoque in response_estoque['Results']['Result']:
                if datetime.strptime(estoque['Data_Validade'], '%d/%m/%Y').date() >= datetime.now().date():
                    values = {'ID_Remedio': estoque['ID_Remedio']}
                    response_remedio = self.get_remedios(values)
                    if response_remedio['Response'][0] == 200:
                        estoque['Remedio'] = response_remedio['Results']['Result'][0]
                        response['Results']['Result'].append(estoque)
                else:
                    values={'ID': estoque['ID']}
                    self._del_estoque(values)
                    
            
        return response

    def _del_estoque(self, value:dict):
        del_estoque = {'function': 'Delete','table_name': 'estoque', 'where': self._normalize_type(value, 'where')}
        response = self.response_in_server(del_estoque)
        return response

    #validar com Luiz
    def get_receita_remedio(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Receita' in value.keys() and isinstance(value['ID_Receita'], int):
            values = {
                'ID_Receita': value['ID_Receita'],
                'Retirada': False
            }
            get_receita_remedio = {'function': 'Select','table_name': 'receita_remedio', 'where': self._normalize_type(values, 'where')}
            response_receita_remedio = self.response_in_server(get_receita_remedio)
            if response_receita_remedio['Response'][0] == 200:
                for receita_remedio in response_receita_remedio['Results']['Result']:
                    values = {'ID_Remedio': receita_remedio['ID_Remedio']}
                    self.get_remedios(values)
                response = response_receita_remedio
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
