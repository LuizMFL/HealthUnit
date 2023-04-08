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
            'Get_Consultas_Disponiveis': self.response_in_CS,
            'Get_Consultas_Realizadas': self.response_in_CS,
            'Get_Consultas_Reservadas': self.response_in_CS,
            'Reservar_Consulta': self.response_in_CS,
            'Del_Consulta_Reservada': self.response_in_CS,
            'Insert_Avaliacao_Profissional': self.insert_avaliacao_profissional,
            'Del_Avaliacao_Profissional': self.del_avaliacao_profissional,
            'Insert_Avaliacao_Unidade': self.insert_avaliacao_unidade,
            'Del_Avaliacao_Unidade': self.del_avaliacao_unidade,
            'Insert_Doenca_Paciente': self.insert_doenca_paciente,
            'Del_Doenca_Paciente': self.del_doenca_paciente,
            'Get_Receita': self.get_receita,
            'Get_Receita': self.get_receita_remedio
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
            response = self.response_in_server(set_aval)
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
            cpf = value['CPF']
            response_get_pa =  self.get_paciente({'CPF': cpf})
            if response_get_pa['Response'][0] == 200 and len(response_get_pa['Results']['Result']):
                del_pe = {'function': 'Delete','table_name': 'pessoa', 'where': self._normalize_type({'CPF': cpf}, 'where')}
                del_pa = {'function': 'Delete','table_name': 'paciente', 'where': self._normalize_type({'ID_Pessoa': response_get_pa['Results']['Result'][0]['ID']}, 'where')}
                response = self.response_in_server(del_pa)
                self.response_in_server(del_pe)
        return response
    

    def get_paciente(self, value:dict):
        response = {'Response': (406, 'Failed'), 'Results':{'Result':[]}}
        if 'CPF' in value.keys() and isinstance(value['CPF'], str):
            cpf = value['CPF']
            if len(cpf) == 11:
                response_pe = self._get_pessoa(cpf)
                response = response_pe
                if response_pe['Response'][0] == 200 and len(response_pe['Results']['Result']):
                    id_pe = response_pe['Results']['Result'][0]['ID']
                    get_pa = {'function': 'Select','table_name': 'paciente', 'where': self._normalize_type({'ID_Pessoa': id_pe}, 'where')}
                    response_pa = self.response_in_server(get_pa)
                    response = response_pa
                    if len(response_pa['Results']['Result']):
                        id_pa = response_pa['Results']['Result'][0].pop('ID')
                        for key in response_pe['Results']['Result'][0].keys():
                            response['Results']['Result'][0][key] = response_pe['Results']['Result'][0][key]
                        response['Results']['Result'][0]['ID'] = id_pa
        return response
    
    def _get_pessoa(self, cpf:str):
        get_pe = {'function': 'Select','table_name': 'pessoa', 'where': self._normalize_type({'CPF': cpf}, 'where')}
        response = self.response_in_server(get_pe)
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
        if 'CPF' in value.keys() and isinstance(value['CPF'], str) and len(value['CPF']) == 11:
            response_pe = self._cadastro_pe(value)
            response = response_pe
            if response_pe['Results']['Response'][0] == 200:
                id_pessoa = self._get_pessoa(value['CPF'])['Results']['Result'][0]['ID']
                set_pa = {'function': 'Insert', 'table_name': 'paciente', 'values': self._normalize_type({'ID_Pessoa': id_pessoa}, 'values')}
                response_pa = self.response_in_server(set_pa)
                response = response_pa
        return response

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


if __name__ == '__main__':
    p = Paciente()
    a = p.cadastro_pa({'CPF': '10154389450', 'Nome': 'Francisco', 'Telefone': '81999932153', 'Email': 'luis.sda.3dqda@gmail.com', 'CEP': '51394123', 'Complem_Endereco': 'dasdadaNADa','Idade': 1, 'Genero': 'H', 'Nascimento': '15-03-2001'})
    print(a)
    b = p.get_paciente({'CPF':'10154389450'})
    print(b)
    c = p.get_consultas_realizadas({'CPF':'10154389450'})
    print(c)