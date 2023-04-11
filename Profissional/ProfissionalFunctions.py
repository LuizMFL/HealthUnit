import socket
import json
import re
from contextlib import contextmanager

class Profissional:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Del_Pessoa': self.del_pessoa, # CPF ou ID_Pessoa
            #'Get_Profissional': self.get_profissional,
            'Cadastro_Profissional': self.cadastro_profissional, # Todas informações da Pessoa e Profissão que deseja
            'Update_Pe': self.update_pe,
            'Get_Avaliacoes_Profissional': self.get_avaliacoes_profissional,
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
    
    def cadastro_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str) and len(value['CPF']) >= 11 and 'Profissao' in value.keys() and isinstance(value['Profissao'], str):
            response_pe = self._cadastro_pe(value)
            if response_pe['Results']['Response'][0] == 200 and response_pe['Results']['Response'][0] == 200:
                id_pessoa = self._get_pessoa(value['CPF'])['Results']['Result'][0]['ID']
                values = {'ID_Pessoa': id_pessoa}
                response_pr = self._cadastro_pr(values)
                if response_pr['Response'][0] == 200 and response_pr['Results']['Response'][0] == 200:
                    id_profissional = self._get_profissional(values)['Results']['Result'][0]['ID']
                    values = {'ID_Profissional': id_profissional}
                    set_pr = {'function': 'Insert', 'table_name': value['Profissao'], 'values': self._normalize_type(values, 'values')}
                    response_pr = self.response_in_server(set_pr)
                    if response_pr['Response'][0] == 200 and response_pr['Results']['Response'][0] == 200:
                        response = response_pr
                    else:
                        values = {'ID_Pessoa': id_pessoa}
                        self.del_pessoa()
        return response
    
    def del_pessoa(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            values = {'CPF': value['CPF']}
            del_pe = {'function': 'Delete','table_name': 'pessoa', 'where': self._normalize_type(values, 'where')}
            response_pa = self.response_in_server(del_pe)
            if response_pa['Response'][0] == 200:
                response = response_pa
        elif 'ID_Pessoa' in value.keys() and isinstance(value['ID_Pessoa'], int):
            values = {'ID': value['ID_Pessoa']}
            del_pe = {'function': 'Delete','table_name': 'pessoa', 'where': self._normalize_type(values, 'where')}
            response_pa = self.response_in_server(del_pe)
            if response_pa['Response'][0] == 200:
                response = response_pa
        return response
    
    def _get_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        get_pr = ''
        if 'ID_Pessoa' in value.keys() and isinstance(value['ID_Pessoa'], int):
            values = {'ID_Pessoa': value['ID_Pessoa']}
            get_pr = {'function': 'Select','table_name': 'profissional', 'where': self._normalize_type(values, 'where')}
        elif 'ID_Profissional' in value.keys() and isinstance(value['ID_Profissional'], int):
            values = {'ID_Pessoa': value['ID_Pessoa']}
            get_pr = {'function': 'Select','table_name': 'profissional', 'where': self._normalize_type(values, 'where')}
        if not get_pr == '':
            response_pr = self.response_in_server(get_pr)
            if response_pr['Response'][0] == 200:
                response = response_pr
        return response

    def get_medico(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            cpf = value['CPF']
            if len(cpf) == 11:
                response_pe = self._get_pessoa(cpf)
                if response_pe['Response'][0] == 200 and len(response_pe['Results']['Result']):
                    id_pe = response_pe['Results']['Result'][0]['ID']
                    response_pr = self._get_profissional(id_pe)
                    if response_pr['Response'][0] == 200 and len(response_pr['Results']['Result']):
                        id_pr = response_pe['Results']['Result'][0]['ID_Pessoa']
                        get_md = {'function': 'Select','table_name': 'medico', 'where': self._normalize_type({'ID_Profissional': id_pr}, 'where')}
                        response_md = self.response_in_server(get_md)
                        response = response_md
                        if len(response_md['Results']['Result']):
                            id_md = response_md['Results']['Result'][0].pop('ID')
                            for key in response_pe['Results']['Result'][0].keys():
                                response['Results']['Result'][0][key] = response_pe['Results']['Result'][0][key]
                            response['Results']['Result'][0]['ID'] = id_md
        return response
    
    def get_avaliacoes_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Profissional' in value.keys() and isinstance(value['ID_Profissional'], int):
            values = {'ID_Profissional': value['ID_Profissional']}
            get_aval_prof = {'function': 'Select','table_name': 'avaliacao_profissional', 'where': self._normalize_type(values, 'where')}
            response_aval_prof = self.response_in_server(get_aval_prof)
            if response_aval_prof['Response'][0] == 200:
                for aval_prof in response_aval_prof['Results']['Result']:
                    get_paciente = {'function': 'Get_Paciente', 'values': {'ID_Paciente': aval_prof['ID_Paciente']}}
                    response_paciente = self.response_in_server(get_paciente, 'PC')
                    

            
    def _get_pessoa(self, cpf:str):
        get_pe = {'function': 'Select','table_name': 'pessoa', 'where': self._normalize_type({'CPF': cpf}, 'where')}
        response = self.response_in_server(get_pe)
        return response
    
    def _get_profissional(self, id_pessoa:int):
        get_pr = {'function': 'Select','table_name': 'profissional', 'where': self._normalize_type({'ID_Pessoa': id_pessoa}, 'where')}
        response = self.response_in_server(get_pr)
        return response

    def _cadastro_pr(self, value:dict):
        set_pr = {'function': 'Insert', 'table_name': 'profissional', 'values': self._normalize_type(value, 'values')}
        response_pr = self.response_in_server(set_pr)
        return response_pr
    
    def _cadastro_pe(self, value:dict):
        set_pe = {'function': 'Insert', 'table_name': 'pessoa', 'values': self._normalize_type(value, 'values')}
        response_pe = self.response_in_server(set_pe)
        return response_pe
    
    def update_pe(self, value:dict): 
        value_w = {}
        if 'CPF' in value.keys():
            value_w['CPF'] = value.pop('CPF')
        if 'ID' in value.keys():
            value_w['ID'] = value.pop('CPF')
        response = {'Response': (406, 'Failed')}
        if value_w.keys():
            upd_pe = {'function': 'Update', 'table_name': 'pessoa', 'where': self._normalize_type(value_w, 'where'), 'values': self._normalize_type(value, 'values')}
            response_pe = self.response_in_server(upd_pe)
            response = response_pe
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


    def get_consultas_realizadas(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            cpf = value['CPF']
            response_get_md =  self.get_medico(cpf)
            if response_get_md['Response'][0] == 200 and len(response_get_md['Results']['Result']):
                id_md = response_get_md['Results']['Result'][0]['ID']
            
    def get_consultas_realizadas(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            cpf = value['CPF']
            response_get_md =  self.get_medico(cpf)
            if response_get_md['Response'][0] == 200 and len(response_get_md['Results']['Result']):
                id_md = response_get_md['Results']['Result'][0]['ID']
                get_con_md = {'function': 'Select','table_name': 'consulta_medico_reservada', 'where': self._normalize_type({'ID_Medico': id_md}, 'where')}
                response_get_con_md = self.response_in_server(get_con_md)
                response = {'Response': (200, 'Success!'), 'Results':{'Result': []}}
                for consulta_md in response_get_con_md['Results']['Result']:
                    id_con = consulta_md['ID_Consulta']
                    get_con = {'function': 'Select','table_name': 'consulta', 'where': self._normalize_type({'ID': id_con}, 'where')}
                    response_get_con = self.response_in_server(get_con)
                    if response_get_con['Response'][0] == 200 and len(response_get_con['Results']['Result']):
                        response['Results']['Result'].append(response_get_con['Results']['Result'][0])
                    else:
                        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
                        break
        return response
