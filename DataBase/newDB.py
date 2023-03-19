import pymysql.cursors
from contextlib import contextmanager
from pathlib import Path
from Functions import json_tools
import os
from time import strftime, ctime, time

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
        self.Create_DB()
        
    def Create_DB(self):
        with self.connect_LocalHost() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW DATABASES;')
                existing_db = cursor.fetchall()
                existing_db = [x['Database'] for x in existing_db]
                if not self.config['db_name'] in existing_db:
                    self._Backup_DB_Import(True)


    def _Backup_DB_Export(self):
        backups = []
        maximo_dir = 6
        for dir in Path(self.PATH_DataSets + r'\Backups').iterdir():
            if dir.is_file():
                tempo = os.path.getctime(dir)
                backups.append((dir, tempo))
        backups = sorted(backups, key=lambda x: x[1])
        backups_remove = backups[:len(backups) - maximo_dir]
        for backup_remove in backups_remove:
            os.remove(backup_remove[0])
        filestamp = strftime(r'%d_%m_%Y_%H_%M_%S')
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
        os.system('mysqldump -h %s -u %s --password=%s %s < %s' % (self.config['host'], self.config['user'], self.config['password'], self.config['db_name'], dump_name))

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
    def connect_DB(self, DB_name:str):
        conn = pymysql.connect(
            host=self.config['host'],
            user=self.config['user'],
            password=self.config['password'],
            db=DB_name,
            charset=self.config['charset'],
            cursorclass=self.config['cursorclass']  # Quando fizermos uma consulta, teremos um DICT
        )
        try:
            yield conn  # Vai retornar a conexão e continuar quando for chamda de novo
        finally:
            conn.close()

if __name__ == "__main__":
    db = DataBase()
    db._Backup_DB_Export()
