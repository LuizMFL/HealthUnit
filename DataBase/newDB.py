import pymysql
from contextlib import contextmanager
from pathlib import Path
from Functions import *
import os
from datetime import datetime, date, time

class DataBase:
    def __init__(self) -> None:
        self.PATH_DataSets = str(Path(__file__).parent / 'Datasets')
        self.config = {
            'user': 'root',
            'password': 'Lu1zM1gu3l#My$QL',
            'host': 'localhost',
            'cursorclass': pymysql.cursors.DictCursor,
            'charset': 'utf8mb4',
            'db_name': 'healthunit'
        }
        self.tables_functions = {
            'pessoa': None,
            'paciente': None,
            'profissional': None,
            'medico': None,
            'avaliacao_profissional': None,
            'avaliacao_unidade': None,
            'especializacao': None,
            'especializacao_medico': None,
            'recepcionista': None,
            'farmaceutico': None,
            'doenca': None,
            'remedio': None,
            'doenca_remedio': None,
            'doenca_paciente': None,
            'estoque': None,
            'calendario': None,
            'calendario_especializacao_medico': None,
            'consulta': None,
            'consulta_disponivel': None,
            'consulta_paciente_reservada': None,
            'receita': None,
            'receita_remedio': None
        }
        self.Create_DB()

    def Select(self, value:dict):
        with self.connect_DB() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW TABLES;')
                existing_tables = cursor.fetchall()
                existing_tables = [x[f'Tables_in_{self.config["db_name"]}'] for x in existing_tables]
                if value['table_name'] in existing_tables:
                    value = self.Select_Informations_Column(value, cursor)
                    informations = tuple(value.pop('Result'))
                    where = ' WHERE '
                    sequence_column = []
                    informations = {x['COLUMN_NAME']:{'DATA_TYPE': x['DATA_TYPE'], 'COLUMN_TYPE': x['COLUMN_TYPE']} for x in informations}
                    for column in value['where']:
                        if column['name'] in informations.keys():
                            typ = informations[column['name']]['DATA_TYPE']
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date.today() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            if not (isinstance(column['value'], type(typ)) and column['operator'] in ['=', '>', '<', '>=', '<=', '<>']):
                                value['Response'] = (406, 'Operator Error')
                                return value
                            where += f'{column["name"]} {column["operator"]} ' + '%s, '
                            sequence_column.append(column['value'])
                        else:
                            value['Response'] = (406, 'Column Name Error')
                            return value
                    sequence_column = tuple(sequence_column)
                    where = where[:-2]if len(value['where']) else ''
                    sql = f'SELECT * FROM {value["table_name"]}{where};'
                    try:
                        cursor.execute(sql, sequence_column)
                        value['Response'] = (200, 'Select Success')
                    except Exception as e:
                        value['Response'] = (406, e)
                    value['Result'] = tuple(cursor.fetchall())
                else:
                    value['Response'] = (406, 'Table Name Error')
                    return value
        return value
    
    def Insert(self, value:dict):
        with self.connect_DB() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW TABLES;')
                existing_tables = cursor.fetchall()
                existing_tables = [x[f'Tables_in_{self.config["db_name"]}'] for x in existing_tables]
                if value['table_name'] in existing_tables:
                    value = self.Select_Informations_Column(value, cursor)
                    informations = value.pop('Result')
                    informations = {x['COLUMN_NAME']:{'DATA_TYPE': x['DATA_TYPE'], 'COLUMN_TYPE': x['COLUMN_TYPE'], 'COLUMN_KEY': x['COLUMN_KEY']} for x in informations}
                    sql1 = f'INSERT INTO {value["table_name"]} ('
                    sql2 = ') VALUES ('
                    sequence_column = []
                    for column in value['values']:
                        if column['name'] in informations.keys():
                            typ = informations[column['name']]['DATA_TYPE']
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date.today() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            if not isinstance(column['value'], type(typ)):
                                value['Response'] = (406, 'Type Value Error')
                                return value
                            sql1 += f'{column["name"]}, '
                            sql2 += '%s, '
                            sequence_column.append(column['value'])
                        else:
                            value['Response'] = (406, 'Column Name Error')
                            return value
                    sql = sql1[:-2] + sql2[:-2] + ');'
                    sequence_column = tuple(sequence_column)
                    try:
                        cursor.execute(sql, sequence_column)
                        value['Response'] = (200, 'Insert Success')
                    except pymysql.err.IntegrityError as e:
                        conn.rollback()
                        value['Response'] = (406, 'Integrity Error')
                    except pymysql.err.DataError as e:
                        conn.rollback()
                        value['Response'] = (406, e)
                    conn.commit()
                    value['Result'] = tuple(cursor.fetchall())
                else:
                    value['Response'] = (406, 'Table Name Error')
                    return value
        return value
    
    #! CONTINUE UPDATE
    def Update(self, value:dict):
        with self.connect_DB() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW TABLES;')
                existing_tables = cursor.fetchall()
                existing_tables = [x[f'Tables_in_{self.config["db_name"]}'] for x in existing_tables]
                if value['table_name'] in existing_tables:
                    value = self.Select_Informations_Column(value, cursor)
                    informations = value.pop('Result')
                    
                    informations = {x['COLUMN_NAME']:{'DATA_TYPE': x['DATA_TYPE'], 'COLUMN_TYPE': x['COLUMN_TYPE'], 'COLUMN_KEY':x['COLUMN_KEY'], 'EXTRA':x['EXTRA']} for x in informations}
                    informations_locked = {x:y for x,y in informations.items() if y['COLUMN_KEY'] in ['UNI', 'PRI', 'MUL']}
                    informations_locked_where = {x:y for x,y in informations_locked.items() if y['COLUMN_KEY'] == 'PRI'} if len({x:y for x,y in informations_locked.items() if y['COLUMN_KEY'] == 'PRI'}) else informations_locked
                    print(informations)
                    print()
                    print(informations_locked)
                    print()
                    print(informations_locked_where)
                    
                    sql1 = f'UPDATE {value["table_name"]} SET '
                    sql2 = ' WHERE '
                    sequence_column = []
                    for column in value['values']:
                        if column['name'] in informations.keys():
                            typ = informations[column['name']]['DATA_TYPE']
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date.today() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            if not isinstance(column['value'], type(typ)):
                                value['Response'] = (406, 'Type Value Error')
                                return value
                            elif column['name'] in informations_locked.keys():
                                value['Response'] = (406, f'Update Error In Column {informations_locked[column["name"]]["COLUMN_KEY"]}')
                            sql1 += f'{column["name"]} = ' + '%s, '
                            sequence_column.append(column['value'])
                        else:
                            value['Response'] = (406, 'Column Name Error')
                            return value
                    list_column_locked = {}
                    for column in value['where']:
                        if column['name'] in informations.keys():
                            typ = informations[column['name']]['DATA_TYPE']
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date.today() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            if not (isinstance(column['value'], type(typ)) and column['operator'] in ['=', '>', '<', '>=', '<=', '<>']):
                                value['Response'] = (406, 'Operator Error')
                                return value
                            sql2 += f'{column["name"]} {column["operator"]} ' + '%s, '
                            sequence_column.append(column['value'])
                        else:
                            value['Response'] = (406, 'Column Name Error')
                            return value
                    sql = sql1[:-2] + sql2[:-2] + ';'
                    print(sql)
                    sequence_column = tuple(sequence_column)
                    try:
                        cursor.execute(sql, sequence_column)
                        value['Response'] = (200, 'Insert Success')
                    except pymysql.err.IntegrityError as e:
                        conn.rollback()
                        value['Response'] = (406, 'Integrity Error')
                    except pymysql.err.DataError as e:
                        conn.rollback()
                        value['Response'] = (406, e)
                    conn.commit()
                    value['Result'] = tuple(cursor.fetchall())
                else:
                    value['Response'] = (406, 'Table Name Error')
                    return value
        return value
    
    def Select_Informations_Column(self, value:dict, cursor=None):
        sql = 'SELECT column_name, data_type, column_type, character_maximum_length, is_nullable, column_key, extra FROM information_schema.columns WHERE table_name = %s;'
        if cursor:
            cursor.execute(sql, (value['table_name']))
            value['Result'] = cursor.fetchall()
        else:
            with self.connect_DB() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (value['table_name']))
                    value['Result'] = cursor.fetchall()
        return value
    
    def Create_DB(self):
        with self.connect_LocalHost() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW DATABASES;')
                existing_db = cursor.fetchall()
                existing_db = [x['Database'] for x in existing_db]
                if not self.config['db_name'] in existing_db:
                    cursor.execute(f'CREATE DATABASE {self.config["db_name"]};')
        self._Backup_DB_Import(True)


    def _Backup_DB_Export(self):
        backups = []
        maximo_dir = 6
        for dir in Path(self.PATH_DataSets + r'\Backups').iterdir():
            if dir.is_file():
                tempo = os.path.getctime(dir)
                backups.append((dir, tempo))
        backups = sorted(backups, key=lambda x: x[1])
        i = len(backups) - maximo_dir 
        backups_remove = backups[:i if i >= 0 else 0]
        for backup_remove in backups_remove:
            os.remove(backup_remove[0])
        filestamp = datetime.now().strftime(r'%d_%m_%Y_%H_%M_%S')
        dump_name = f'{self.PATH_DataSets}\Backups\Backup_{self.config["db_name"]}_{filestamp}.sql'
        os.system('mysqldump -h %s -u %s --password=%s %s > %s' % (self.config['host'], self.config['user'], self.config['password'], self.config['db_name'], dump_name))
    
    def _Backup_DB_Import(self, default_schema:bool=False):
        dump_name = self.PATH_DataSets + r'\struct.sql'
        if not default_schema:
            newer_backup = ('', 0)
            for dir in Path(self.PATH_DataSets + r'\Backups').iterdir():
                if dir.is_file():
                    tempo = os.path.getctime(dir)
                    if tempo >= newer_backup[1]:
                        newer_backup = (dir, tempo)
                        dump_name = dir
        os.system('mysql -h %s -u %s --password=%s %s < %s' % (self.config['host'], self.config['user'], self.config['password'], self.config['db_name'], dump_name))

    @contextmanager
    def connect_LocalHost(self):
        conn = pymysql.connect(
            host=self.config['host'],
            user=self.config['user'],
            password=self.config['password'],
            charset=self.config['charset'],
            cursorclass=self.config['cursorclass'])
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def connect_DB(self):
        conn = pymysql.connect(
            host=self.config['host'],
            user=self.config['user'],
            password=self.config['password'],
            db=self.config['db_name'],
            charset=self.config['charset'],
            cursorclass=self.config['cursorclass']  # Quando fizermos uma consulta, teremos um DICT
        )
        try:
            yield conn  # Vai retornar a conexão e continuar quando for chamda de novo
        finally:
            conn.close()

if __name__ == "__main__":
    db = DataBase()
    #db._Backup_DB_Export()

    b = db.Insert({'table_name': 'pessoa', 'where': [], 'values':[{'name':'CPF', 'value': '10854389458'}, {'name':'Nome', 'value':'Marcos'}, {'name':'Telefone', 'value':'81999496154'}, {'name':'Email', 'value': 'Luiz.sadadsadaakdajdadkasjdahdadkasskdad'}, {'name':'CEP', 'value':'51231333'}, {'name': 'Genero', 'value':'F'}, {'name':'Nascimento', 'value': date(2001, 4, 20)}, {'name': 'Complem_Endereco', 'value': 'Afonso'}, {'name': 'Idade', 'value': 15}]})
    
    print(f'{b["Response"]} -> {b["Result"]}')
    a = db.Select({'table_name': 'pessoa', 'where': [{'name': 'CPF', 'operator': '=', 'value': '10854389458'}]})
    print(f'{a["Response"]} -> {a["Result"]}')
    a = db.Update({'table_name': 'pessoa', 'values': [{'name':'Nome', 'value': 'Rodrigo'}],'where': [{'name': 'CPF', 'operator':'=', 'value':'10854389458'}, {'name': 'Nome', 'operator':'=', 'value':'Marcos'}]})
    print(f'{a["Response"]} -> {a["Result"]}')
    a = db.Select({'table_name': 'pessoa', 'where': [{'name': 'CPF', 'operator': '=', 'value': '10854389458'}]})
    print(f'{a["Response"]} -> {a["Result"]}')