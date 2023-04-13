import socket
import json
import re
from contextlib import contextmanager

class Paciente:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Del_Pessoa': self.del_pessoa, # ID_Pessoa ou CPF
            'Get_Paciente': self.get_paciente, # ID_Paciente ou CPF
            'Cadastro_Paciente': self.cadastro_pa,
            'Update_Pe': self.update_pe, # ID_Pessoa 
            'Insert_Avaliacao_Profissional': self.insert_avaliacao_profissional, # ID_Paciente, ID_Profissional, Nota e Opcional Descrição
            'Update_Avaliacao_Profissional': self.update_avaliacao_profissional, # ID_Avaliacao_Profissional e Opcionais Nota e Descrição
            'Del_Avaliacao_Profissional': self.del_avaliacao_profissional, # ID_Avaliacao_Profissional
            'Insert_Avaliacao_Unidade': self.insert_avaliacao_unidade, # ID_Paciente, Nota e Opcional Descrição
            'Update_Avaliacao_Unidade': self.update_avaliacao_unidade, # ID_Avaliacao_Unidade e Opcionais Nota e Descrição
            'Del_Avaliacao_Unidade': self.del_avaliacao_unidade, # ID_Avaliacao_Unidade
            #'Insert_Doenca_Paciente': self.insert_doenca_paciente, #! Não vale a pena
            #'Get_Doenca_Paciente': self.get_doenca_paciente,  #! Não vale a pena
            #'Del_Doenca_Paciente': self.del_doenca_paciente, #! Não vale a pena
        }
        
    def Select_function(self, value:dict):
        try:
            self.server = value['Servidores']
            print('Passou')
            if value['function'] in self.functions.keys():
                print('Tem function')
                value = self.functions[value['function']](value['values'])
            else:
                value['Response'] = (406, "Function not Exists")
                value['Result'] = ()
        except Exception as e:
            print('Exception ->', e)
            if isinstance(value, dict):
                print('ERRR ->', value)
                value['Response'] = (406, 'Dict Format Error')
                value['Result'] = ()
            else:
                value = {'Response': (406, 'Data Type Error'), 'Result': ()}
        return value
    
    def insert_avaliacao_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int) and 'ID_Profissional' in value.keys() and isinstance(value['ID_Profissional'], int) and 'Nota' in value.keys() and isinstance(value['Nota'], int) and 0 <= value['Nota'] <= 100:
            values= {
                'ID_Paciente': value['ID_Paciente'],
                'ID_Profissional': value['ID_Profissional'],
                'Nota': value['Nota']
            }
            if 'Descricao' in value.keys() and isinstance(value['Descricao'], str):
                values['Descricao'] = value['Descricao']
            set_aval = {'function': 'Insert', 'table_name': 'avaliacao_profissional', 'values': self._normalize_type(values, 'values')}
            response_aval = self.response_in_server(set_aval)
            if response_aval['Response'] == 200:
                response = response_aval
        return response

    def update_avaliacao_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Avaliacao_Profissional' in value.keys() and isinstance(value['ID_Avaliacao_Profissional'], int) and 'Nota' in value.keys() and isinstance(value['Nota'], int) and 0 <= value['Nota'] <= 100:
            values_w = {
                'ID': value['ID_Avaliacao_Profissional']
            }
            values_u = {
                'Nota': value['Nota']
            }
            if 'Descricao' in value.keys() and isinstance(value['Descricao'], str):
                values_u['Descricao'] = value['Descricao']
            upd_aval = {'function': 'Update','table_name': 'avaliacao_profissional', 'where': self._normalize_type(values_w, 'where'), 'values': self._normalize_type(values_u, 'values')}
            response_up = self.response_in_server(upd_aval)
            if response_up['Response'][0] == 200:
                response = response_up
        return response
    
    def del_avaliacao_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Avaliacao_Profissional' in value.keys() and isinstance(value['ID_Avaliacao_Profissional'], int):
            values= {
                'ID': value['ID_Avaliacao_Profissional']
            }
            del_aval = {'function': 'Delete','table_name': 'avaliacao_profissional', 'where': self._normalize_type(values, 'where')}
            response_del = self.response_in_server(del_aval)
            if response_del['Response'][0] == 200:
                response = response_del
        return response

    def insert_avaliacao_unidade(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int) and 'Nota' in value.keys() and isinstance(value['Nota'], int) and 0 <= value['Nota'] <= 100:
            values= {
                'ID_Paciente': value['ID_Paciente'],
                'Nota': value['Nota']
            }
            if 'Descricao' in value.keys() and isinstance(value['Descricao'], str):
                values['Descricao'] = value['Descricao']
            set_aval = {'function': 'Insert', 'table_name': 'avaliacao_unidade', 'values': self._normalize_type(values, 'values')}
            response_aval = self.response_in_server(set_aval)
            if response_aval['Response'][0] == 200:
                response = response_aval
        return response

    def update_avaliacao_unidade(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Avaliacao_Unidade' in value.keys() and isinstance(value['ID_Avaliacao_Unidade'], int) and 'Nota' in value.keys() and isinstance(value['Nota'], int) and 0 <= value['Nota'] <= 100:
            values_w = {
                'ID': value['ID_Avaliacao_Unidade']
            }
            values_u = {
                'Nota': value['Nota']
            }
            if 'Descricao' in value.keys() and isinstance(value['Descricao'], str):
                values_u['Descricao'] = value['Descricao']
            upd_aval = {'function': 'Update','table_name': 'avaliacao_unidade', 'where': self._normalize_type(values_w, 'where'), 'values': self._normalize_type(values_u, 'values')}
            response_aval = self.response_in_server(upd_aval)
            if response_aval['Response'][0] == 200:
                response = response_aval
        return response
    
    def del_avaliacao_unidade(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Avaliacao_Unidade' in value.keys() and isinstance(value['ID_Avaliacao_Unidade'], int):
            values = {
                'ID': value['ID_Avaliacao_Unidade']
            }
            del_aval = {'function': 'Delete','table_name': 'avaliacao_unidade', 'where': self._normalize_type(values, 'where')}
            response_aval = self.response_in_server(del_aval)
            if response_aval['Response'][0] == 200:
                response = response_aval
        return response
    
    def insert_doenca_paciente(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int) and 'ID_Doenca' in value.keys() and isinstance(value['ID_Doenca'], int):
            values= {
                'ID_Paciente': value['ID_Paciente'],
                'ID_Doenca': value['ID_Doenca']
            }
            set_do_pa = {'function': 'Insert', 'table_name': 'doenca_paciente', 'values': self._normalize_type(values, 'values')}
            response_do_pa = self.response_in_server(set_do_pa)
            if response_do_pa['Response'][0] == 200:
                response = response_do_pa
        return response
    
    def get_doenca_paciente(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int):
            values = {
                'ID_Paciente': value['ID_Paciente']
            }
            get_doe_pa = {'function': 'Select','table_name': 'doenca_paciente', 'where': self._normalize_type(values, 'where')}
            response = self.response_in_server(get_doe_pa)
        return response
    
    def del_doenca_paciente(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int) and 'ID_Doenca' in value.keys() and isinstance(value['ID_Doenca'], int):
            values= {
                'ID_Paciente': value['ID_Paciente'],
                'ID_Doenca': value['ID_Doenca']
            }
            del_do_pa = {'function': 'Delete','table_name': 'doenca_paciente', 'where': self._normalize_type(values, 'where')}
            response = self.response_in_server(del_do_pa)
        return response
    
    def del_pessoa(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            values = {'CPF': value['CPF']}
            response_pe = self._get_pessoa(values)
            values = {}
            if response_pe['Response'][0] == 200 and len(response_pe['Results']['Result']):
                values = {'ID': response_pe['Results']['Result'][0]['ID']}
        elif 'ID_Pessoa' in value.keys() and isinstance(value['ID_Pessoa'], int):
            values = {'ID': value['ID_Pessoa']}
        del_pe = {'function': 'Delete','table_name': 'pessoa', 'where': self._normalize_type(values, 'where')}
        if len(values.keys()):
            response_pe = self.response_in_server(del_pe)
            if response_pe['Response'][0] == 200:
                response = response_pe
        return response
    
    def get_paciente(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            values = {'CPF': value['CPF']}
            response_pe = self._get_pessoa(values)
            if response_pe['Response'][0] == 200 and len(response_pe['Results']['Result']):
                values = {'ID_Pessoa': response_pe['Results']['Result'][0]['ID']}
                get_pa = {'function': 'Select','table_name': 'paciente', 'where': self._normalize_type(values, 'where')}
                response_pa = self.response_in_server(get_pa)
                if response_pa['Response'][0] == 200 and len(response_pa['Results']['Result']):
                    response = response_pa
                    id_pa = response_pa['Results']['Result'][0]['ID']
                    for key in response_pe['Results']['Result'][0].keys():
                        response['Results']['Result'][0][key] = response_pe['Results']['Result'][0][key]
                    response['Results']['Result'][0]['ID'] = id_pa
        elif 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int):
            values = {'ID': value['ID_Paciente']}
            get_pa = {'function': 'Select','table_name': 'paciente', 'where': self._normalize_type(values, 'where')}
            response_pa = self.response_in_server(get_pa)
            if response_pa['Response'][0] == 200 and len(response_pa['Results']['Result']):
                values['ID'] = response_pa['Results']['Result'][0]['ID_Pessoa']
                response_pe = self._get_pessoa(values)
                if response_pe['Response'][0] == 200:
                    response = response_pa
                    id_pa = response_pa['Results']['Result'][0]['ID']
                    for key in response_pe['Results']['Result'][0].keys():
                        response['Results']['Result'][0][key] = response_pe['Results']['Result'][0][key]
                    response['Results']['Result'][0]['ID'] = id_pa
                else:
                    response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        return response
    
    def _get_pessoa(self, value:dict):
        get_pe = {'function': 'Select','table_name': 'pessoa', 'where': self._normalize_type(value, 'where')}
        response = self.response_in_server(get_pe)
        return response
    
    def get_receitas(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int):
            values = {
                'ID_Paciente': value['ID_Paciente']
            }
            get_rec = {'function': 'Select','table_name': 'receita', 'where': self._normalize_type(values, 'where')}
            response_rec = self.response_in_server(get_rec)
            for n, receita in enumerate(response_rec['Results']['Result']):
                values = {
                    'ID_Receita': receita['ID']
                }
                response_rec_rem = self.get_receita_remedio(value)
                if response_rec_rem['Response'] == 200:
                    remedios = [{'ID_Remedio': x['ID_Remedio'], 'Quantidade': x['Quantidade'], 'Retirada': x['Retirada']} for x in response_rec_rem['Results']['Result']]
                    response_rec_rem['Results']['Result'][n]['Remedios'] = remedios
        return response
    
    def get_receita_remedio(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Receita' in value.keys() and isinstance(value['ID_Receita'], int):
            values = {
                'ID_Receita': values['ID_Receita']
            }
            get_rec_rem = {'function': 'Select','table_name': 'receita_remedio', 'where': self._normalize_type(values, 'where')}
            response_rec_rem = self.response_in_server(get_rec_rem)
            response = response_rec_rem
        return response

    def cadastro_pa(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}} 
        if 'CPF' in value.keys() and isinstance(value['CPF'], str) and len(value['CPF']) >= 11:
            response_pe = self._cadastro_pe(value)
            if response_pe['Response'][0] == 200 and response_pe['Results']['Response'][0] == 200:
                values = {'CPF': value['CPF']}
                id_pessoa = self._get_pessoa(values)['Results']['Result'][0]['ID']
                values = {'ID_Pessoa': id_pessoa}
                set_pa = {'function': 'Insert', 'table_name': 'paciente', 'values': self._normalize_type(values, 'values')}
                response_pa = self.response_in_server(set_pa)
                if response_pa['Response'][0] == 200 and response_pa['Results']['Response'][0] == 200:
                        response = response_pa
                else:
                    self.del_pessoa(values)
        return response

    def _cadastro_pe(self, value:dict):
        set_pe = {'function': 'Insert', 'table_name': 'pessoa', 'values': self._normalize_type(value, 'values')}
        response_pe = self.response_in_server(set_pe)
        return response_pe

    def update_pe(self, value:dict): 
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        value_w = {}
        if 'CPF' in value.keys():
            value.pop('CPF')
        if 'ID_Pessoa' in value.keys():
            id_pessoa = value.pop('ID_Pessoa')
            if isinstance(id_pessoa, int):
                value_w['ID'] = id_pessoa
        if 'ID' in value.keys():
            value.pop('ID')
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
                correct = ''
                if key in ['CPF', 'Telefone', 'CEP']:
                    correct = '[^0-9]'
                elif key in ['Nome', 'Genero']:
                    correct = '[^a-zA-Z ]'
                elif key == 'Nascimento':
                    correct =  '[^0-9/]'
                elif key == 'Email':
                    correct = '[^a-zA-Z0-9@.]'
                elif key in ['Complem_Endereco', 'Descricao']:
                    correct = '[^a-zA-Z0-9.-/:?]'
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
            sock.settimeout(10)
            sock.connect(self.server[server_name])
            yield sock
            sock.close()
        except Exception as e:
            print(f'ERROR -> {e}')
