import socket
import json
import re
from contextlib import contextmanager
from datetime import datetime
from threading import Thread
from time import sleep

class Reserva:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Reservar_Receita': self.reservar_receita,
            'Get_Receitas_Reservadas': self.get_receitas_reservadas, # ID_Paciente ou CPF e Opcional ID_Consulta
        }
        self.Reservar_ID_Receita = []
        self.Thread_Reservando = Thread(target=self._reservar_receita, args=(self,), daemon=True)
        self.Thread_Reservando.start()
        
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

    def reservar_receita(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Receita' in value.keys() and isinstance(value['ID_Receita'], int):
            values = {'ID_Receita': value['ID_Receita']}
            response_reserva = self._get_receita_reservada(values)
            if response_reserva['Response'][0] == 200 and len(response_reserva['Results']['Result']) == 0:
                self.Reservar_ID_Receita.append(values['ID_Receita'])
                response['Response'] = (200, 'Success')
        return response
    
    def _reservar_receita(x, self):
        print('THREAD _RESERVAR_RECEITA COMEÇOU')
        while True:
            print(f'Lista de ID_Receita para Reservar: {self.Reservar_ID_Receita}')
            if len(self.Reservar_ID_Receita):
                values = {'ID_Receita': self.Reservar_ID_Receita.pop(0)}
                get_receita_remedio = {'function': 'Get_Receita_Remedio', 'values': values}
                response_receita_remedio = self.response_in_server(get_receita_remedio, 'FC')
                if response_receita_remedio['Response'][0] == 200:
                    qtd = len(response_receita_remedio['Results']['Result'])
                    for receita_remedio in response_receita_remedio['Results']['Result']:
                        values_r = {'ID_Remedio': receita_remedio['ID_Remedio']}
                        get_estoque_remedio = {'function': 'Get_Estoque', 'values': values_r}
                        response_estoque_remedio = self.response_in_server(get_estoque_remedio, 'FC')
                        quantidade = 0
                        for estoque_remedio in response_estoque_remedio['Results']['Result']:
                            quantidade += estoque_remedio['Quantidade']
                        if receita_remedio['Quantidade'] <= quantidade:
                            qtd -= 1
                    if qtd == 0:
                        set_receita_reservada = {'function': 'Insert','table_name': 'receita_reservada', 'values': self._normalize_type(values, 'values')}
                        response_estoque_remedio = self.response_in_server(set_receita_reservada)
                    else:
                        self.Reservar_ID_Receita.append(values['ID_Receita'])
            sleep(5)

    def get_receitas_reservadas(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        get_paciente = {'function': 'Get_Paciente', 'values': value}
        response_paciente = self.response_in_server(get_paciente, 'PC')
        if response_paciente['Response'][0] == 200 and response_paciente['Results']['Response'] == 200 and len(response_paciente['Results']['Result']):
            response_paciente['Results']['Result'][0]['Receitas'] = []
            values = {'ID_Paciente': response_paciente['Results']['Result'][0]['ID']}
            get_receita = {'function': 'Select','table_name': 'receita', 'where': self._normalize_type(values, 'where')}
            response_receita = self.response_in_server(get_receita)
            if response_receita['Response'][0] == 200:
                for receita in response_receita['Results']['Result']:
                    values = {'ID_Receita': receita['ID']}
                    response_reserva = self._get_receita_reservada(values)
                    if response_reserva['Response'][0] == 200 and len(response_reserva['Results']['Result']): #? Vai entregar a receita reservada e se ela já foi inteiramente Retirada
                        receita['Retirada'] = response_reserva['Results']['Result'][0]['Retirada']
                        if datetime.strptime(receita['Data_Validade'], '%d/%m/%Y').date() >= datetime.now().date():
                            response_paciente['Results']['Result'][0]['Receitas'].append(receita)
                        else:
                            self._del_receita_reservada(values)
                response = response_paciente
        return response
    
    def _del_receita_reservada(self, value:dict):
        del_receita = {'function': 'Delete','table_name': 'receita_reservada', 'where': self._normalize_type(value, 'where')}
        response = self.response_in_server(del_receita)
        return response

    def _get_receita_reservada(self, value:dict):
        get_receita = {'function': 'Select','table_name': 'receita_reservada', 'where': self._normalize_type(value, 'where')}
        response_reserva = self.response_in_server(get_receita)
        return response_reserva
    
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
