import pymysql
from contextlib import contextmanager
from pathlib import Path
import os
from datetime import datetime, date, time
from ctypes import c_uint8 as tinyint, c_uint16 as smallint, c_uint, c_uint32, c_uint64
import re
class DataBase:
    def __init__(self) -> None:
        self.PATH_DataSets = str(Path(__file__).parent / 'Datasets')
        self.config = {
            'user': 'root',
            'password': 'lucas0519',
            'host': 'localhost',
            'cursorclass': pymysql.cursors.DictCursor,
            'charset': 'utf8mb4',
            'db_name': 'healthunit'
        }
        self.functions = {
            'Insert': self._Insert,
            'Select': self._Select,
            'Update': self._Update,
            'Delete': self._Delete,
            'Backup': self._Select_Backup
        }
        self.types = {
            'tinyint unsigned': tinyint,
            'smallint unsigned': smallint,
            'mediumint unsigned': c_uint32,
            'int unsigned': c_uint32
        }
        self._Create_DB()

    def Select_function(self, value:dict) -> dict:
        try:
            if value['function'] in self.functions.keys():
                value = self.functions[value['function']](value)
            else:
                value['Response'] = (406, "Function not Exists")
                value['Result'] = ()
            
            if 'values' in value.keys():
                for i, dict_value in enumerate(value['values']):
                    if 'value' in dict_value.keys():
                        if isinstance(dict_value['value'], type(date.today())):
                            value['values'][i]['value'] = dict_value['value'].strftime('%d/%m/%Y')
                        elif isinstance(dict_value['value'], type(time.max)):
                            value['values'][i]['value'] = dict_value['value'].strftime('%H:%M:%S')
            value['Result'] = tuple(value['Result'])
            for i, dict_result in enumerate(value['Result']):
                for key in dict(dict_result).keys():
                    if isinstance(dict_result[key], type(date.today())):
                        value['Result'][i][key] = dict_result[key].strftime('%d/%m/%Y')
                    elif isinstance(dict_result[key], type(time.max)):
                        value['Result'][i][key] = dict_result[key].strftime('%H:%M:%S')
            value['Result'] = tuple(value['Result'])
        except Exception:
            if isinstance(value, dict):
                value['Response'] = (406, 'Dict Format Error')
                value['Result'] = ()
            else:
                value = {'Result': (), }
                
        return value
    
    def _Select_Backup(self, value:dict) -> dict:
        if value['values'][0]['name'] == 'Export':
            try:
                self._Backup_DB_Export()
                value['Response'] = (200, 'Export Success')
            except Exception as e:
                value['Response'] = (406, f'Export Error: {e}')
        else:
            try:
                self._Backup_DB_Import()
                value['Response'] = (200, 'Import Success')
            except Exception as e:
                value['Response'] = (406, f'Import Error: {e}')
        value['Result'] = ()
        return value
        
    def _Select(self, value_Original:dict) -> dict:
        value = dict(value_Original)
        value_Original['Result'] = ()
        with self.connect_DB() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW TABLES;')
                existing_tables = cursor.fetchall()
                existing_tables = [x[f'Tables_in_{self.config["db_name"]}'] for x in existing_tables]
                value['Result'] = ()
                if value['table_name'] in existing_tables:
                    value = self._Select_Informations_Column(value, cursor)
                    informations = tuple(value.pop('Result'))
                    informations = {x['COLUMN_NAME']:{'DATA_TYPE': x['DATA_TYPE'], 'COLUMN_TYPE': x['COLUMN_TYPE']} for x in informations}
                    value['Result'] = ()
                    where = ' WHERE '
                    sequence_column = []
                    for column in value['where']:
                        if column['name'] in informations.keys():
                            typ = informations[column['name']]['DATA_TYPE']
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date.today() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            if isinstance(typ, type(date.today())):
                                try:
                                    column['value'] = datetime.strptime(column['value'], '%d/%m/%Y').date()
                                except Exception:
                                    value_Original['Response'] = (406, 'Format Date Error')
                                    return value_Original
                            elif isinstance(typ, type(time.max)):
                                try:
                                    column['value'] = datetime.strptime(column['value'], '%H:%M:%S').time()
                                except Exception:
                                    value_Original['Response'] = (406, 'Format Date Error')
                                    return value_Original
                            if not (isinstance(column['value'], type(typ)) and column['operator'] in ['=', '>', '<', '>=', '<=', '<>']):
                                value_Original['Response'] = (406, 'Value Type or Operator Error')
                                return value
                            elif 'unsigned' in informations[column['name']]['COLUMN_TYPE']:
                                unsignedtype = self.types[informations[column['name']]['COLUMN_TYPE']]
                                max_unsigned = unsignedtype(-1)
                                if 'medium' in informations[column['name']]['COLUMN_TYPE']:
                                    max_unsigned = c_uint(16777215)
                                max_unsigned = c_uint(max_unsigned.value)
                                if not (0 <= column['value'] and c_uint64(column['value']).value <= max_unsigned.value):
                                    value_Original['Response'] = (406, 'Value Type not in Range of Type Operator Error')
                                    return value_Original
                            where += f'{column["name"]} {column["operator"]} ' + '%s AND '
                            sequence_column.append(column['value'])
                        else:
                            value_Original['Response'] = (406, 'Column Name Error')
                            return value_Original
                    sequence_column = tuple(sequence_column)
                    where = where[:-5]if len(value['where']) else ''
                    sql = f'SELECT * FROM {value["table_name"]}{where};'
                    try:
                        cursor.execute(sql, sequence_column)
                        value_Original['Response'] = (200, 'Select Success')
                    except Exception as e:
                        value_Original['Response'] = (406, e)
                    value_Original['Result'] = tuple(cursor.fetchall())
                else:
                    value_Original['Response'] = (406, 'Table Name Error')
                    return value_Original
        return value_Original
    
    def _Insert(self, value_Original:dict) -> dict:
        value = dict(value_Original)
        value_Original['Result'] = ()
        with self.connect_DB() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW TABLES;')
                existing_tables = cursor.fetchall()
                existing_tables = [x[f'Tables_in_{self.config["db_name"]}'] for x in existing_tables]
                value['Result'] = ()
                if value['table_name'] in existing_tables:
                    value = self._Select_Informations_Column(value, cursor)
                    informations = value.pop('Result')
                    informations = {x['COLUMN_NAME']:{'DATA_TYPE': x['DATA_TYPE'], 'COLUMN_TYPE': x['COLUMN_TYPE'], 'COLUMN_KEY': x['COLUMN_KEY']} for x in informations}
                    value['Result'] = ()
                    sql1 = f'INSERT INTO {value["table_name"]} ('
                    sql2 = ') VALUES ('
                    sequence_column = []
                    for column in value['values']:
                        if column['name'] in informations.keys():
                            typ = informations[column['name']]['DATA_TYPE']
                            typ_ = str(typ)
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date.today() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            
                            if typ_ in ['char', 'varchar']:
                                column_type = informations[column['name']]['COLUMN_TYPE']
                                tam = int(re.sub('[^0-9]', '', column_type))
                                if typ_ == 'varchar':
                                    if not 0 < len(column['value']) < tam:
                                        value_Original['Response'] = (406, f'{column_type} Lenght Error')
                                        return value_Original
                                else:
                                    if not len(column['value']) == tam:
                                        value_Original['Response'] = (406, f'{column_type} Lenght Error')
                                        return value_Original
                            elif isinstance(typ, type(date.today())):
                                try:
                                    column['value'] = datetime.strptime(column['value'], '%d/%m/%Y').date()
                                except Exception:
                                    value_Original['Response'] = (406, 'Format Date Error')
                                    return value_Original
                            elif isinstance(typ, type(time.max)):
                                try:
                                    column['value'] = datetime.strptime(column['value'], '%H:%M:%S').time()
                                except Exception:
                                    value_Original['Response'] = (406, 'Format Date Error')
                                    return value_Original
                            if not isinstance(column['value'], type(typ)):
                                value_Original['Response'] = (406, 'Value Type Error')
                                return value_Original
                            elif 'unsigned' in informations[column['name']]['COLUMN_TYPE']:
                                unsignedtype = self.types[informations[column['name']]['COLUMN_TYPE']]
                                max_unsigned = unsignedtype(-1)
                                if 'medium' in informations[column['name']]['COLUMN_TYPE']:
                                    max_unsigned = c_uint(16777215)
                                max_unsigned = c_uint(max_unsigned.value)
                                if not (0 <= column['value'] and c_uint64(column['value']).value <= max_unsigned.value):
                                    value_Original['Response'] = (406, 'Value Type not in Range of Type Operator Error')
                                    return value_Original
                            sql1 += f'{column["name"]}, '
                            sql2 += '%s, '
                            sequence_column.append(column['value'])
                        else:
                            value_Original['Response'] = (406, 'Column Name Error')
                            return value_Original
                    sql = sql1[:-2] + sql2[:-2] + ');'
                    sequence_column = tuple(sequence_column)
                    try:
                        cursor.execute(sql, sequence_column)
                        value_Original['Response'] = (200, 'Insert Success')
                    except pymysql.err.IntegrityError as e:
                        conn.rollback()
                        value_Original['Response'] = (406, 'Integrity Error')
                    except pymysql.err.DataError as e:
                        conn.rollback()
                        value_Original['Response'] = (406, str(e))
                    conn.commit()
                    value_Original['Result'] = tuple(cursor.fetchall())
                else:
                    value_Original['Response'] = (406, 'Table Name Error')
                    return value_Original
        return value_Original
    
    def _Update(self, value_Original:dict) -> dict:
        value = dict(value_Original)
        value_Original['Result'] = ()
        with self.connect_DB() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW TABLES;')
                existing_tables = cursor.fetchall()
                existing_tables = [x[f'Tables_in_{self.config["db_name"]}'] for x in existing_tables]
                value['Result'] = ()
                if value['table_name'] in existing_tables:
                    value = self._Select_Informations_Column(value, cursor)
                    informations = value.pop('Result')
                    informations = {x['COLUMN_NAME']:{'DATA_TYPE': x['DATA_TYPE'], 'COLUMN_TYPE': x['COLUMN_TYPE'], 'COLUMN_KEY':x['COLUMN_KEY'], 'EXTRA':x['EXTRA']} for x in informations}
                    informations_locked = {x:y for x,y in informations.items() if y['COLUMN_KEY'] in ['UNI', 'PRI', 'MUL']}
                    informations_locked_where = {x:y for x,y in informations_locked.items() if y['COLUMN_KEY'] == 'PRI'} if len({x:y for x,y in informations_locked.items() if y['COLUMN_KEY'] == 'PRI'}) else informations_locked
                    value['Result'] = ()
                    sql1 = f'UPDATE {value["table_name"]} SET '
                    sql2 = ' WHERE '
                    sequence_column = []
                    for column in value['values']:
                        if column['name'] in informations.keys():
                            typ = informations[column['name']]['DATA_TYPE']
                            typ_ = str(typ)
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date.today() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            if typ_ in ['char', 'varchar']:
                                column_type = informations[column['name']]['COLUMN_TYPE']
                                tam = int(re.sub('[^0-9]', '', column_type))
                                if typ_ == 'varchar':
                                    if not 0 < len(column['value']) < tam:
                                        value_Original['Response'] = (406, f'{column_type} Lenght Error')
                                        return value_Original
                                else:
                                    if not len(column['value']) == tam:
                                        value_Original['Response'] = (406, f'{column_type} Lenght Error')
                                        return value_Original
                            elif isinstance(typ, type(date.today())):
                                try:
                                    column['value'] = datetime.strptime(column['value'], '%d/%m/%Y').date()
                                except Exception:
                                    value_Original['Response'] = (406, 'Format Date Error')
                                    return value_Original
                            elif isinstance(typ, type(time.max)):
                                try:
                                    column['value'] = datetime.strptime(column['value'], '%H:%M:%S').time()
                                except Exception:
                                    value_Original['Response'] = (406, 'Format Date Error')
                                    return value_Original
                            if not isinstance(column['value'], type(typ)):
                                value_Original['Response'] = (406, 'Value Type Error')
                                return value_Original
                            elif 'unsigned' in informations[column['name']]['COLUMN_TYPE']:
                                unsignedtype = self.types[informations[column['name']]['COLUMN_TYPE']]
                                max_unsigned = unsignedtype(-1)
                                if 'medium' in informations[column['name']]['COLUMN_TYPE']:
                                    max_unsigned = c_uint(16777215)
                                max_unsigned = c_uint(max_unsigned.value)
                                if not (0 <= column['value'] and c_uint64(column['value']).value <= max_unsigned.value):
                                    value_Original['Response'] = (406, 'Value Type not in Range of Type Operator Error')
                                    return value_Original
                            if column['name'] in informations_locked.keys():
                                value_Original['Response'] = (406, f'Update Error In Column {informations_locked[column["name"]]["COLUMN_KEY"]}')
                                return value_Original
                            sql1 += f'{column["name"]} = ' + '%s, '
                            sequence_column.append(column['value'])
                        else:
                            value_Original['Response'] = (406, 'Column Name Error')
                            return value_Original
                    for column in value['where']:
                        if column['name'] in informations.keys():
                            typ = informations[column['name']]['DATA_TYPE']
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date.today() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            if isinstance(typ, type(date.today())):
                                try:
                                    column['value'] = datetime.strptime(column['value'], '%d/%m/%Y').date()
                                except Exception:
                                    value_Original['Response'] = (406, 'Format Date Error')
                                    return value_Original
                            elif isinstance(typ, type(time.max)):
                                try:
                                    column['value'] = datetime.strptime(column['value'], '%H:%M:%S').time()
                                except Exception:
                                    value_Original['Response'] = (406, 'Format Date Error')
                                    return value_Original
                            if not (isinstance(column['value'], type(typ)) and column['operator'] == '='):
                                value_Original['Response'] = (406, 'Value Type or Operator Error')
                                return value_Original
                            elif 'unsigned' in informations[column['name']]['COLUMN_TYPE']:
                                unsignedtype = self.types[informations[column['name']]['COLUMN_TYPE']]
                                max_unsigned = unsignedtype(-1)
                                if 'medium' in informations[column['name']]['COLUMN_TYPE']:
                                    max_unsigned = c_uint(16777215)
                                max_unsigned = c_uint(max_unsigned.value)
                                if not (0 <= column['value'] and c_uint64(column['value']).value <= max_unsigned.value):
                                    value_Original['Response'] = (406, 'Value Type not in Range of Type Operator Error')
                                    return value_Original
                            if column['name'] in informations_locked_where.keys():
                                informations_locked_where.pop(column['name'])
                            else: 
                                value_Original['Response'] = (406, 'Where Whit Not Unique or Primary Column Error')
                                return value_Original
                            sql2 += f'{column["name"]} {column["operator"]} ' + '%s AND '
                            sequence_column.append(column['value'])
                        else:
                            value_Original['Response'] = (406, 'Column Name Error')
                            return value_Original
                    if informations_locked_where:
                        value_Original['Response'] = (406, 'Columns Unique or Primary Not Satisfated Error')
                    else:
                        sql = sql1[:-2] + sql2[:-5] + ';'
                        sequence_column = tuple(sequence_column)
                        try:
                            cursor.execute(sql, sequence_column)
                            value_Original['Response'] = (200, 'Update Success')
                        except pymysql.err.IntegrityError as e:
                            conn.rollback()
                            value_Original['Response'] = (406, 'Integrity Error')
                        except pymysql.err.DataError as e:
                            conn.rollback()
                            value_Original['Response'] = (406, e)
                        conn.commit()
                        value_Original['Result'] = tuple(cursor.fetchall())
                else:
                    value_Original['Response'] = (406, 'Table Name Error')
                    return value_Original
        return value_Original
    
    def _Delete(self, value_Original:dict) -> dict:
        value = dict(value_Original)
        value_Original['Result'] = ()
        with self.connect_DB() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW TABLES;')
                existing_tables = cursor.fetchall()
                existing_tables = [x[f'Tables_in_{self.config["db_name"]}'] for x in existing_tables]
                value['Result'] = ()
                if value['table_name'] in existing_tables:
                    value = self._Select_Informations_Column(value, cursor)
                    informations = value.pop('Result')
                    informations = {x['COLUMN_NAME']:{'DATA_TYPE': x['DATA_TYPE'], 'COLUMN_TYPE': x['COLUMN_TYPE'], 'COLUMN_KEY':x['COLUMN_KEY'], 'EXTRA':x['EXTRA']} for x in informations}
                    informations_locked = {x:y for x,y in informations.items() if y['COLUMN_KEY'] in ['UNI', 'PRI', 'MUL']}
                    informations_locked_where = {x:y for x,y in informations_locked.items() if y['COLUMN_KEY'] == 'PRI'} if len({x:y for x,y in informations_locked.items() if y['COLUMN_KEY'] == 'PRI'}) else informations_locked
                    value['Result'] = ()
                    sql = f'DELETE FROM {value["table_name"]} WHERE '
                    sequence_column = []
                    for column in value['where']:
                        if column['name'] in informations.keys():
                            typ = informations[column['name']]['DATA_TYPE']
                            typ = int() if str(typ).count('int') else typ
                            typ = str() if str(typ).count('char') or str(typ).count('text') else typ
                            typ = date.today() if str(typ).count('date') else typ
                            typ = time() if str(typ).count('time') else typ
                            if isinstance(typ, type(date.today())):
                                try:
                                    column['value'] = datetime.strptime(column['value'], '%d/%m/%Y').date()
                                except Exception:
                                    value_Original['Response'] = (406, 'Format Date Error')
                                    return value_Original
                            elif isinstance(typ, type(time.max)):
                                try:
                                    column['value'] = datetime.strptime(column['value'], '%H:%M:%S').time()
                                except Exception:
                                    value_Original['Response'] = (406, 'Format Time Error')
                                    return value_Original
                            if not (isinstance(column['value'], type(typ)) and column['operator'] == '='):
                                value_Original['Response'] = (406, 'Value Type or Operator Error')
                                return value_Original
                            elif 'unsigned' in informations[column['name']]['COLUMN_TYPE']:
                                unsignedtype = self.types[informations[column['name']]['COLUMN_TYPE']]
                                max_unsigned = unsignedtype(-1)
                                if 'medium' in informations[column['name']]['COLUMN_TYPE']:
                                    max_unsigned = c_uint(16777215)
                                max_unsigned = c_uint(max_unsigned.value)
                                if not (0 <= column['value'] and c_uint64(column['value']).value <= max_unsigned.value):
                                    value_Original['Response'] = (406, 'Value Type not in Range of Type Operator Error')
                                    return value_Original
                            if column['name'] in informations_locked_where.keys():
                                informations_locked_where.pop(column['name'])
                            else: 
                                value_Original['Response'] = (406, 'Where Whit Not Unique or Primary Column Error')
                                return value_Original
                            sql += f'{column["name"]} {column["operator"]} ' + '%s AND '
                            sequence_column.append(column['value'])
                        else:
                            value_Original['Response'] = (406, 'Column Name Error')
                            return value_Original
                    sequence_column = tuple(sequence_column)
                    sql = sql[:-5] + ';'
                    try:
                        cursor.execute(sql, sequence_column)
                        value_Original['Response'] = (200, 'Delete Success')
                    except pymysql.err.IntegrityError as e:
                        conn.rollback()
                        value_Original['Response'] = (406, 'Integrity Error')
                    except pymysql.err.DataError as e:
                        conn.rollback()
                        value_Original['Response'] = (406, e)
                    conn.commit()
                    value_Original['Result'] = tuple(cursor.fetchall())
                else:
                    value_Original['Response'] = (406, 'Table Name Error')
                    return value_Original
        return value_Original
    
    def _Select_Informations_Column(self, value:dict, cursor=None) -> dict:
        sql = 'SELECT column_name, data_type, column_type, character_maximum_length, is_nullable, column_key, extra FROM information_schema.columns WHERE table_schema = %s AND table_name = %s;'
        dados = (self.config['db_name'], value['table_name'])
        if cursor:
            cursor.execute(sql, dados)
            value['Result'] = cursor.fetchall()
        else:
            with self.connect_DB() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, dados)
                    value['Result'] = cursor.fetchall()
        return value
    
    def _Create_DB(self) -> None:
        with self.connect_LocalHost() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW DATABASES;')
                existing_db = cursor.fetchall()
                existing_db = [x['Database'] for x in existing_db]
                if not self.config['db_name'] in existing_db:
                    cursor.execute(f'CREATE DATABASE {self.config["db_name"]};')
        self._Backup_DB_Import(True)


    def _Backup_DB_Export(self) -> None:
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
    
    def _Backup_DB_Import(self, default_schema:bool=False) -> None:
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
    #? Examples:
    a = db.Select_function({'function': 'Insert','table_name': 'pessoa', 'where': [], 'values':[{'name':'CPF', 'value': '10854389451'}, {'name':'Nome', 'value':'Marcos'}, {'name':'Telefone', 'value':'81999496154'}, {'name':'Email', 'value': 'Luiz.sadadsadaakdajdadkasjdahdadkasskdad'}, {'name':'CEP', 'value':'51231333'}, {'name': 'Genero', 'value':'F'}, {'name':'Nascimento', 'value': '20/03/2000'}, {'name': 'Complem_Endereco', 'value': 'Afonso'}, {'name': 'Idade', 'value': 15}]})
    print(f'{a["Response"]} -> {a["Result"]}')
    a = db.Select_function({'function': 'Update', 'table_name': 'pessoa', 'values': [{'name':'Nome', 'value': 'Rodrigo'}],'where': [{'name': 'ID', 'operator':'=', 'value':3}]})
    print(f'{a["Response"]} -> {a["Result"]}')
    a = db.Select_function({'function': 'Delete','table_name': 'pessoa', 'where': [{'name': 'CPF', 'operator': '=', 'value': '10854389458'}]})
    print(f'{a["Response"]} -> {a["Result"]}')
    a = db.Select_function({'function': 'Select','table_name': 'pessoa', 'where': []})
    print(f'{a["Response"]} -> {a["Result"]}')
    a = db.Select_function({'function': 'Backup', 'values': [{'name': 'Export'}]})
    print(f'{a["Response"]} -> {a["Result"]}')
    a = db.Select_function({'function': 'Backup', 'values': [{'name': 'Import'}]})
    print(f'{a["Response"]} -> {a["Result"]}')
    