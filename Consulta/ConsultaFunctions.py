import socket
import json
import re
from contextlib import contextmanager
from datetime import datetime, date
from time import gmtime
class Consulta:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Get_Calendarios': self.get_calendarios, # {'Atual': bool}
            #'Insert_Calendario_Especializacao_Medico': self.insert_calendario_especializacao_medico, #? # Adicionar uma data ao calendario e Cria tambem as consultas com um tempo xxmin de cada consulta e elas são todas disponiveis
            #'Del_Calendario_Especializacao_Medico': self.del_calendario_especializacao_medico,
            'Insert_Consulta_Disponivel': self.insert_consulta_disponivel, # ID_Consulta e se ela estiver nas consultas Reservadas e NÃO realizadas ele é colocado como disponível
            'Get_Consultas_Disponiveis': self.get_consultas_disponiveis, # Sempre que chamada irá deletar as consultas que tiverem o tempo inicial menor ou igual do tempo atual e data atual
            'Get_Consultas_Reservadas': self.get_consultas_reservadas, # Receber também o bool para definir se é uma consulta Realizada ou não
            'Get_Consultas_Especializacao_Disponiveis': self.get_consultas_especializacao_disponiveis, # Usar o get_consultas disponiveis, Especialização é OPCIONAL
            'Reservar_Consulta': self.reservar_consulta, # Deleta a consulta disponivel com o mesmo ID e adiciona ela à Reservada
            'Confirmar_Consulta': self.confirmar_consulta
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
    
    def insert_consulta_disponivel(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Consulta' in value.keys() and isinstance(value['ID_Consulta'], int):
            values = {'ID_Consulta': value['ID_Consulta']}
            response_consulta_reservada = self.get_consultas_reservadas(values)
            if response_consulta_reservada['Response'][0] == 200 and len(response_consulta_reservada['Results']['Result']):
                if not response_consulta_reservada['Results']['Result'][0]['Realizada']:
                    set_cons_disp = {'function': 'Insert', 'table_name': 'consulta_disponivel', 'values': self._normalize_type(values, 'values')}
                    response_cons_disp = self.response_in_server(set_cons_disp)
                    if response_cons_disp['Response'][0] == 200:
                        del_cons_res = {'function': 'Delete', 'table_name': 'consulta_paciente_reservada', 'where': self._normalize_type(values, 'where')}
                        self.response_in_server(del_cons_res)
                        response = response_cons_disp
        return response

    def get_consultas_reservadas(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'ID_Consulta' in value.keys() and isinstance(value['ID_Consulta'], int):
            values = {'ID_Consulta': value['ID_Consulta']}
        elif 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int):
            values = {'ID_Paciente': value['ID_Paciente']}
        if 'Realizada' in value.keys() and isinstance(value['Realizada'], bool):
            values['Realizada'] =  value['Realizada']
        if len(values.keys()):
            get_cons_reservadas = {'function': 'Select', 'table_name': 'consulta_paciente_reservada', 'where': self._normalize_type(values, 'where')}
            response_cons_reserv = self.response_in_server(get_cons_reservadas)
            if response_cons_reserv['Response'][0] == 200:
                for cons_reserv in response_cons_reserv['Results']['Result']:
                    values = {'ID_Consulta': cons_reserv['ID_Consulta']}
                    response_consulta = self._get_consultas(values)
                    if response_consulta['Response'][0] == 200:
                        response_consulta['Results']['Result'][0].pop('ID')
                        values = {'ID_Consult'}
    
    def get_calendarios(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'Atual' in value.keys() and isinstance(value['Atual'], bool):
            get_calen = {'function': 'Select', 'table_name': 'calendario', 'where': []}
            response_calen = self.response_in_server(get_calen)
            if value['Atual']:
                data_atual = datetime.today().date()
                response_calen['Results']['Result'] = [x for x in response_calen['Results']['Result'] if datetime.strptime(x['Data_Calendar'], '%d/%m/%Y').date() >= data_atual]
            response = response_calen
        elif 'ID_Calendario' in value.keys() and isinstance(value['ID_Calendario'], int):
            values = {'ID': value['ID_Calendario']}
            get_calen = {'function': 'Select', 'table_name': 'calendario', 'where': self._normalize_type(values, 'where')}
            response_calen = self.response_in_server(get_calen)
            response = response_calen
        return response
    
    #!
    def _insert_calendario(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'Data_Calendar' in value.keys() and isinstance(value['Data_Calendar'], str):
            data_atual = datetime.today().date()
            try:
                data = datetime.strptime(value['Data_Calendar'], '%d/%m/%Y').date()
                if data >= data_atual:
                    weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    values = {
                        'Data_Calendar': value['Data_Calendar'],
                        'Dia_Semana': weekday[data.weekday()]
                    }
                    set_calen = {'function': 'Insert', 'table_name': 'calendario', 'values': self._normalize_type(values, 'values')}
                    response = self.response_in_server(set_calen)
            except Exception:
                pass
        return response
    #!
    def insert_calendario_especializacao_medico(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        response_calen = self._insert_calendario(value)
        if response_calen['Response'] == 200:
            data_atual = datetime.today().date()
            try:
                data = datetime.strptime(value['Data_Calendar'], '%d/%m/%Y').date()
                if data >= data_atual:
                    weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    values = {
                        'Data_Calendar': value['Data_Calendar'],
                        'Dia_Semana': weekday[data.weekday()]
                    }
                    set_calen = {'function': 'Insert', 'table_name': 'calendario', 'values': self._normalize_type(values, 'values')}
                    response = self.response_in_server(set_calen)
            except Exception:
                pass
        return response
    
    def get_especializacao_medico(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'ID_Especializacao' in value.keys() and isinstance(value['ID_Especializacao'], int):
            values['ID_Especializacao'] = value['ID_Especializacao']
        elif 'ID_Medico' in value.keys() and isinstance(value['ID_Medico'], int):
            values['ID_Medico'] = value['ID_Medico']
        get_esp_med = {'function': 'Select', 'table_name': 'especializacao_medico', 'where': self._normalize_type(values, 'where')}
        self.response_in_server(get_esp_med, 'MD')
        
    def get_consultas_disponiveis(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        get_consulta_disponivel = {'function': 'Select', 'table_name': 'consulta_disponivel', 'where': []}

    def _get_consultas(self, value:dict):
        get_cons = {'function': 'Select', 'table_name': 'consulta', 'where': []}
        response_cons = self.response_in_server(get_cons)
        self.get_calendarios()
        for consu in response_cons['Results']['Result']:
            get_calen = {'function': 'Select', 'table_name': 'calendario', 'where': []}
            ID_Calendario_Especializacao_Medico
    def _atualizar_consultas_disponiveis(self):
        pass
    
    def _normalize_type(self, value:dict, option:str):
        value_aux = []
        #print('Valores recebidos -> ', value)
        for key in value.keys():
            x = value[key]
            if isinstance(x, str):
                correct = '[^a-zA-Z0-9]'
                if key in ['CPF', 'Telefone', 'CEP']:
                    correct = '[^0-9]+'
                elif key == 'Dia_Semana':
                    correct = '[^a-zA-Z ]+'
                elif key == 'Data_Calendar':
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
            response_get_pa =  self.get_paciente(cpf)
            if response_get_pa['Response'][0] == 200 and len(response_get_pa['Results']['Result']):
                id_pa = response_get_pa['Results']['Result'][0]['ID']
            
    def get_consultas_realizadas(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            cpf = value['CPF']
            response_get_pa =  self.get_paciente(cpf)
            if response_get_pa['Response'][0] == 200 and len(response_get_pa['Results']['Result']):
                id_pa = response_get_pa['Results']['Result'][0]['ID']
                get_con_pa = {'function': 'Select','table_name': 'consulta_paciente_reservada', 'where': self._normalize_type({'ID_Paciente': id_pa}, 'where')}
                response_get_con_pa = self.response_in_server(get_con_pa)
                response = {'Response': (200, 'Success!'), 'Results':{'Result': []}}
                for consulta_pa in response_get_con_pa['Results']['Result']:
                    id_con = consulta_pa['ID_Consulta']
                    get_con = {'function': 'Select','table_name': 'consulta', 'where': self._normalize_type({'ID': id_con}, 'where')}
                    response_get_con = self.response_in_server(get_con)
                    if response_get_con['Response'][0] == 200 and len(response_get_con['Results']['Result']):
                        response['Results']['Result'].append(response_get_con['Results']['Result'][0])
                    else:
                        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
                        break
        return response
