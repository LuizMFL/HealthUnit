import pymysql.cursors
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
                    cursor.execute(f'SHOW COLUMNS FROM {value["table_name"]}')
                    existing_columns_in_table = cursor.fetchall()
                    print(existing_columns_in_table)
                    columns_fild_type = {x['Field']: x['Type'] for x in existing_columns_in_table}
                    where = ' WHERE '
                    for column in value['where']:
                        if column['name'] in columns_fild_type.keys():
                            typ = str(columns_fild_type[column['name']])
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            if not (isinstance(column['value'], type(typ)) and column['operator'] in ['=', '>', '<', '>=', '<=', '<>']):
                                value['Response'] = (406, 'Operator Error')
                                return value
                            where += f'{column["name"]} {column["operator"]} {column["value"]}, '
                        else:
                            value['Response'] = (406, 'Column Name Error')
                            return value
                    where = where[:-2] if len(value['where']) else ''
                    sql = 'SELECT * FROM %s%s;' %(value['table_name'], where)
                    print(sql)
                    cursor.execute(sql)
                    value['Result'] = cursor.fetchall()
                else:
                    value['Response'] = (406, 'Table Name Error')
                    return value
        return value
    
    def Insert(self, value:dict):
        with self.connect_DB() as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO pessoa (CPF, Nome, Telefone, Email, CEP, Complem_Endereco, Idade, Genero, Nascimento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', ('10854389458', 'Luiz', '81999496154', 'luiz.m.fad@hamasd', '50810000', 'nada', 20, 'M', date(2002, 3, 15).strftime('%Y-%m-%d')))
                conn.commit()
                """cursor.execute('SHOW TABLES;')
                existing_tables = cursor.fetchall()
                existing_tables = [x[f'Tables_in_{self.config["db_name"]}'] for x in existing_tables]
                where = ''
                if value['table_name'] in existing_tables:
                    cursor.execute(f'SHOW COLUMNS FROM {value["table_name"]}')
                    existing_columns_in_table = cursor.fetchall()
                    print(existing_columns_in_table)
                    columns_fild_type = {x['Field']: x['Type'] for x in existing_columns_in_table}
                    for column in value['where']:
                        if column['name'] in columns_fild_type.keys():
                            typ = str(columns_fild_type[column['name']])
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            if not (isinstance(column['value'], type(typ)) and column['operator'] in ['=', '>', '<', '>=', '<=', '<>']):
                                value['Response'] = (406, 'Operator Error')
                                return value
                            where += f'{column["name"]} {column["operator"]} {column["value"]}, '
                        else:
                            value['Response'] = (406, 'Column Name Error')
                            return value
                    where = where[:-2]
                    cursor.execute('SELECT * FROM %(table_name)s WHERE %(where)s;'  %({'table_name': value['table_name'], 'where':where}))
                    value['Result'] = cursor.fetchall()
                else:
                    value['Response'] = (406, 'Table Name Error')
                    return value
        return value"""
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

    db.Insert({})
    a = db.Select({'table_name': 'pessoa', 'where': []})
    print(a)