import socket
import json
import re
from contextlib import contextmanager

class Profissional:
    def __init__(self) -> None:
        self.server = {}
        self.functions = {
            'Del_Pessoa': self.del_pessoa, # CPF ou ID_Pessoa
            'Get_Profissional': self.get_profissional, # Recebe CPF, ID_Pessoa ou ID_Profissional e entrega Todas informações da Pessoa e do Profissional
            'Cadastro_Profissional': self.cadastro_profissional, # Recebe Todas informações da Pessoa e a Profissão que deseja
            'Update_Pe': self.update_pe,  # Recebe o ID_Pessoa e atualiza as outras informações
            'Get_Avaliacoes_Profissional': self.get_avaliacoes_profissional, # Recebe CPF, ID_Pessoa ou ID_Profissional e entrega Todas informações da Pessoa e do Profissional e do Paciente
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
            table_name = value.pop('Profissao').lower()
            response_pe = self._cadastro_pe(value)
            if response_pe['Results']['Response'][0] == 200 and response_pe['Results']['Response'][0] == 200:
                id_pessoa = self._get_pessoa(value)['Results']['Result'][0]['ID']
                values = {'ID_Pessoa': id_pessoa}
                response_pr = self._cadastro_pr(values)
                if response_pr['Response'][0] == 200 and response_pr['Results']['Response'][0] == 200:
                    id_profissional = self._get_profissional(values)['Results']['Result'][0]['ID']
                    values = {'ID_Profissional': id_profissional}
                    set_pr = {'function': 'Insert', 'table_name': table_name, 'values': self._normalize_type(values, 'values')}
                    response_pr = self.response_in_server(set_pr)
                    if response_pr['Response'][0] == 200 and response_pr['Results']['Response'][0] == 200:
                        response = response_pr
                    else:
                        values = {'ID_Pessoa': id_pessoa}
                        self.del_pessoa(values)
        return response
    
    def get_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if ('CPF' in value.keys() and isinstance(value['CPF'], str)) or ('ID_Pessoa' in value.keys() and isinstance(value['ID_Pessoa'], int)):
            values = {'CPF': value['CPF']}
            response_pe = self._get_pessoa(values)
            if response_pe['Response'][0] == 200 and len(response_pe['Results']['Result']):
                values = {'ID_Pessoa': response_pe['Results']['Result'][0]['ID']}
                response_pr = self._get_profissional(values)
                if response_pr['Response'][0] == 200 and len(response_pr['Results']['Result']):
                    values = {'ID_Profissional': response_pr['Results']['Result'][0]['ID']}
                    response_pr_func = self._get_pr_funcao(values)
                    response = response_pr_func
                    values = {
                        'ID': response['Results']['Result'][0]['ID'],
                        'Profissao': response['Results']['table_name'].title(),
                        'ID_Pessoa': response_pe['Results']['Result'][0]['ID']
                        }
                    for key in response_pe['Results']['Result'][0].keys():
                        response['Results']['Result'][0][key] = response_pe['Results']['Result'][0][key]
                    for key in values.keys():
                        response['Results']['Result'][0][key] = values[key]
        elif 'ID_Profissional' in value.keys() and isinstance(value['ID_Profissional'], int):
            response_pr = self._get_profissional(value)
            if response_pr['Response'][0] == 200 and len(response_pr['Results']['Result']):
                values = {'ID_Pessoa': response_pr['Results']['Result'][0]['ID_Pessoa']}
                response_pe = self._get_pessoa(values)
                response_pr_func = self._get_pr_funcao(value)
                response = response_pr_func
                values = {
                    'ID': response['Results']['Result'][0]['ID'],
                    'Profissao': response['Results']['table_name'].title(),
                    'ID_Pessoa': response_pe['Results']['Result'][0]['ID']
                    }
                for key in response_pe['Results']['Result'][0].keys():
                        response['Results']['Result'][0][key] = response_pe['Results']['Result'][0][key]
                for key in values.keys():
                    response['Results']['Result'][0][key] = values[key]
        return response
    def _get_pr_funcao(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'ID_Profissional' in value.keys() and isinstance(value['ID_Profissional'], int):
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
            response = response_pr 
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
    
    def _get_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'ID_Pessoa' in value.keys() and isinstance(value['ID_Pessoa'], int):
            values = {'ID_Pessoa': value['ID_Pessoa']}
        elif 'ID_Profissional' in value.keys() and isinstance(value['ID_Profissional'], int):
            values = {'ID': value['ID_Profissional']}
        get_pr = {'function': 'Select','table_name': 'profissional', 'where': self._normalize_type(values, 'where')}
        if len(values.keys()):
            response_pr = self.response_in_server(get_pr)
            if response_pr['Response'][0] == 200:
                response = response_pr
        return response
    
    def get_avaliacoes_profissional(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        response_pr = self.get_profissional(value)
        if response_pr['Response'][0] == 200 and len(response_pr['Results']['Result']):
            values = {'ID_Profissional': response_pr['Results']['Result'][0]['ID_Profissional']}
            if 'ID_Paciente' in value.keys():
                values['ID_Paciente'] = value['ID_Paciente']
            get_aval = {'function': 'Select','table_name': 'avaliacoes_profissional', 'where': self._normalize_type(values, 'where')}
            response_aval = self.response_in_server(get_aval)
            if response_aval['Response'][0] == 200:
                response = response_pr
                response['Results']['Result'][0]['Avaliacoes'] = []
                for aval in response_aval['Results']['Result']:
                    values = {'ID_Paciente': aval.pop('ID_Paciente')}
                    aval.pop('ID_Profissional')
                    response_pa = self.response_in_server(values, 'PC') #!
                    if response_pa['Response'][0] == 200:
                        aval['Paciente'] = response_pa['Results']['Result'][0]
                        response['Results']['Result'][0]['Avaliacoes'].append(aval)
                response['Results']['Result'][0]['Avaliacoes'] = response_aval['Results']['Result']
        return response

            
    def _get_pessoa(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        values = {}
        if 'ID_Pessoa' in value.keys() and isinstance(value['ID_Pessoa'], int):
            values = {'ID': value['ID_Pessoa']}
        elif 'CPF' in value.keys() and isinstance(value['CPF'], str):
            values = {'CPF': value['CPF']}
        get_pe = {'function': 'Select','table_name': 'pessoa', 'where': self._normalize_type(values, 'where')}
        if len(values.keys()):
            response_pe = self.response_in_server(get_pe)
            if response_pe['Response'][0] == 200:
                response = response_pe
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
        return value_aux
    
    def _format_result(self, value:dict):
        for key in value.keys():
            if isinstance(value[key], str):
                if key == 'CPF':
                    value[key] = value[key][:3] + '.' + value[key][3:6] + '.' + value[key][6:9] + '-' + value[key][9:]
        return value

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
