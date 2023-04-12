import socket
import json
import re
from contextlib import contextmanager

class Paciente:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Del_Paciente': self.del_paciente,
            'Get_Paciente': self.get_paciente,
            'Cadastro_Paciente': self.cadastro_pa,
            'Update_Pe': self.update_pe,
            'Get_Consultas_Disponiveis': self.response_in_CS, #!
            'Get_Consultas_Realizadas': self.response_in_CS, #!
            'Get_Consultas_Reservadas': self.response_in_CS, #!
            'Reservar_Consulta': self.response_in_CS, #!
            'Del_Consulta_Reservada': self.response_in_CS, #!
            'Insert_Avaliacao_Profissional': self.insert_avaliacao_profissional, 
            'Get_Avaliacao_Profissional': self.get_avaliacao_profissional, 
            'Get_Profissional': self.get_profissional, #!
            'Update_Avaliacao_Profissional': self.update_avaliacao_profissional, #  Continuar daqui
            'Del_Avaliacao_Profissional': self.del_avaliacao_profissional,
            'Insert_Avaliacao_Unidade': self.insert_avaliacao_unidade,
            'Get_Avaliacao_Unidade': self.get_avaliacao_unidade,
            'Update_Avaliacao_Unidade': self.update_avaliacao_unidade,
            'Del_Avaliacao_Unidade': self.del_avaliacao_unidade,
            'Insert_Doenca_Paciente': self.insert_doenca_paciente,
            'Get_Doenca_Paciente': self.get_doenca_paciente,
            'Del_Doenca_Paciente': self.del_doenca_paciente,
            'Get_Receitas': self.get_receitas,
            'Get_Receita_Remedio': self.get_receita_remedio
            #?
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

    def get_avaliacao_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int):
            values['ID_Paciente'] = value['ID_Paciente']
        if  'ID_Profissional' in value.keys() and isinstance(value['ID_Profissional', int]):
            values['ID_Profissional']: value['ID_Profissional']
        if len(values.keys()):
            get_aval = {'function': 'Select','table_name': 'avaliacao_profissional', 'where': self._normalize_type(values, 'where')}
            response_aval = self.response_in_server(get_aval)
            if response_aval['Response'][0] == 200:
                for aval in response_aval['Results']['Result']:
                    values = {'ID_Paciente': aval['ID_Paciente']}
                    response_pa = self.get_paciente(values)
                    values = {'ID_Profissional': aval['ID_Profissional']}
                    response_pr = self.get_profissional(values)
                    if response_pa['Response'][0] == 200 and len(response_pa['Results']['Result']) and response_pr['Response'][0] == 200 and len(response_pr['Results']['Result']):
                        aval.pop('ID_Paciente')
                        aval.pop('ID_Profissional')
                        aval['Paciente'] = response_pa['Results']['Result'][0]
                        aval['Profissional'] = response_pr['Results']['Result'][0]
                response = response_aval
        return response
    
    def get_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if  'ID_Profissional' in value.keys() and isinstance(value['ID_Profissional', int]):
            values = {'ID_Profissional': value['ID_Profissional']}
            get_md = {'function': 'Select','table_name': 'medico', 'where': self._normalize_type(values, 'where')}
            get_far = {'function': 'Select','table_name': 'farmaceutico', 'where': self._normalize_type(values, 'where')}
            get_rec = {'function': 'Select','table_name': 'recepcionista', 'where': self._normalize_type(values, 'where')}
            response_md = self.response_in_server(get_md)
            response_far = self.response_in_server(get_far)
            response_rec = self.response_in_server(get_rec)
            response_pr = {'Response': (406, 'Failed'), 'Results':{'Result':[]}} if not (response_md['Response'][0] == 200 and len(response_md['Results']['Result'])) else response_md
            response_pr = response_pr if not (response_far['Response'][0] == 200 and len(response_far['Results']['Result'])) else response_far
            response_pr = response_pr if not (response_rec['Response'][0] == 200 and len(response_rec['Results']['Result'])) else response_far
            if response_pr['Response'][0] == 200:
                if response_pr['Results']['table_name'] == 'medico':
                    values = {'ID_Medico': response_pr['Results']['Result'][0]['ID']}
                    response_pr = self.get_medico(values)
                    response_pr['Results']['Result'][0]['Profissao'] = 'Medico'
                elif response_pr['Results']['table_name'] == 'recepcionista':
                    values = {'ID_Recepcionista': response_pr['Results']['Result'][0]['ID']}
                    response_pr = self.get_recepcionista(values)
                    response_pr['Results']['Result'][0]['Profissao'] = 'Recepcionista'
                elif response_pr['Results']['table_name'] == 'farmaceutico':
                    values = {'ID_Farmaceutico': response_pr['Results']['Result'][0]['ID']}
                    response_pr = self.get_farmaceutico(values)
                    response_pr['Results']['Result'][0]['Profissao'] = 'Farmaceutico'
                response = response_pr
        return response
    def update_avaliacao_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int) and 'ID_Profissional' in value.keys() and isinstance(value['ID_Profissional', int]) and 'Nota' in value.keys() and isinstance(value['Nota'], int) and 0 <= value['Nota'] <= 100:
            values_w = {
                'ID_Paciente': value['ID_Paciente'],
                'ID_Profissional': value['ID_Profissional']
            }
            values_u = {
                'Nota': value['Nota']
            }
            if 'Descricao' in value.keys() and isinstance(value['Descricao'], str):
                values_u['Descricao'] = value['Descricao']
            upd_aval = {'function': 'Update','table_name': 'avaliacao_profissional', 'where': self._normalize_type(values_w, 'where'), 'values': self._normalize_type(values_u, 'values')}
            response = self.response_in_server(upd_aval)
        return response
    
    def del_avaliacao_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int) and 'ID_Profissional' in value.keys() and isinstance(value['ID_Profissional'], int):
            values= {
                'ID_Paciente': value['ID_Paciente'],
                'ID_Profissional': value['ID_Profissional']
            }
            del_aval = {'function': 'Delete','table_name': 'avaliacao_profissional', 'where': self._normalize_type(values, 'where')}
            response = self.response_in_server(del_aval)
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
            response = self.response_in_server(set_aval)
        return response
    def get_avaliacao_unidade(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int):
            values = {
            'ID_Paciente': value['ID_Paciente']
            }
            get_aval = {'function': 'Select','table_name': 'avaliacao_unidade', 'where': self._normalize_type(values, 'where')}
            response = self.response_in_server(get_aval)
        return response

    def update_avaliacao_unidade(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int) and 'Nota' in value.keys() and isinstance(value['Nota'], int) and 0 <= value['Nota'] <= 100:
            values_w = {
                'ID_Paciente': value['ID_Paciente']
            }
            values_u = {
                'Nota': value['Nota']
            }
            if 'Descricao' in value.keys() and isinstance(value['Descricao'], str):
                values_u['Descricao'] = value['Descricao']
            upd_aval = {'function': 'Update','table_name': 'avaliacao_unidade', 'where': self._normalize_type(values_w, 'where'), 'values': self._normalize_type(values_u, 'values')}
            response = self.response_in_server(upd_aval)
        return response
    
    def del_avaliacao_unidade(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int):
            values= {
                'ID_Paciente': value['ID_Paciente']
            }
            del_aval = {'function': 'Delete','table_name': 'avaliacao_unidade', 'where': self._normalize_type(values, 'where')}
            response = self.response_in_server(del_aval)
        return response
    
    def insert_doenca_paciente(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int) and 'ID_Doenca' in value.keys() and isinstance(value['ID_Doenca'], int):
            values= {
                'ID_Paciente': value['ID_Paciente'],
                'ID_Doenca': value['ID_Doenca']
            }
            set_do_pa = {'function': 'Insert', 'table_name': 'doenca_paciente', 'values': self._normalize_type(values, 'values')}
            response = self.response_in_server(set_do_pa)
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
    
    def del_paciente(self, value:dict):
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

    def get_paciente(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            values = {'CPF': value['CPF']}
            response_pe = self._get_pessoa(values)
            if response_pe['Response'][0] == 200 and len(response_pe['Results']['Result']):
                values = {'ID_Pessoa': response_pe['Results']['Result'][0]['ID']}
                get_pa = {'function': 'Select','table_name': 'paciente', 'where': self._normalize_type(values, 'where')}
                response_pa = self.response_in_server(get_pa)
                if response_pa['Response'][0] == 200:
                    response = response_pa
                    if len(response_pa['Results']['Result']):
                        id_pa = response_pa['Results']['Result'][0]['ID']
                        for key in response_pe['Results']['Result'][0].keys():
                            response['Results']['Result'][0][key] = response_pe['Results']['Result'][0][key]
                        response['Results']['Result'][0]['ID'] = id_pa
        elif 'ID_Paciente' in value.keys() and isinstance(value['ID_Paciente'], int):
            values = {'ID': value['ID_Paciente']}
            get_pa = {'function': 'Select','table_name': 'paciente', 'where': self._normalize_type(values, 'where')}
            response_pa = self.response_in_server(get_pa)
            if response_pa['Response'][0] == 200:
                response = response_pa
                if len(response_pa['Results']['Result']):
                    values['ID'] = response_pa['Results']['Result'][0]['ID_Pessoa']
                    response_pe = self._get_pessoa(values)
                    if response_pe['Response'][0] == 200 and len(response_pe['Results']['Result']):
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

    def reservar_consulta(self, value:dict):
        response = {'Response': (406, 'Failed')}
        if 'ID_Paciente' in value.keys() and value['ID_Paciente'] > 0 and 'ID_Consulta' in value.keys() and value['ID_Consulta'] > 0:
            response_set_con_to_reservada = self.response_in_server({'function': 'Reservar', 'values': {'ID_Paciente': value['ID_Paciente'], 'ID_Consulta': value['ID_Consulta']}}, 'CS')
            response = response_set_con_to_reservada
        return response
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
    def response_in_CS(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID' in value.keys() and isinstance(value['ID'], int):
            id = value['ID']
        return response
    
    def cadastro_pa(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}} 
        print(value)
        print()
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            response_pe = self._cadastro_pe(value)
            print(response_pe)
            print()
            if response_pe['Response'][0] == 200 and response_pe['Results']['Response'][0] == 200:
                values = {'CPF': value['CPF']}
                response_get_pe = self._get_pessoa(values)
                print(response_get_pe)
                print()
                values = {'ID_Pessoa': response_get_pe['Results']['Result'][0]['ID']}
                set_pa = {'function': 'Insert', 'table_name': 'paciente', 'values': self._normalize_type(values, 'values')}
                response_pa = self.response_in_server(set_pa)
                response = response_pa
                if not (response_pa['Response'][0] == 200 and response_pa['Results']['Response'] == 200):
                    values = {'CPF': value['CPF']}
                    self.del_paciente(values)
        return response

    def _cadastro_pe(self, value:dict):
        set_pe = {'function': 'Insert', 'table_name': 'pessoa', 'values': self._normalize_type(value, 'values')}
        response_pe = self.response_in_server(set_pe)
        return response_pe

    def update_pe(self, value:dict): 
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}} 
        value_w = {}
        if 'CPF' in value.keys():
            value_w['CPF'] = value.pop('CPF')
        if 'ID_Pessoa' in value.keys():
            value_w['ID'] = value.pop('CPF')
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
