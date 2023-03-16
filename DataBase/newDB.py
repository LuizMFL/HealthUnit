import pymysql.cursors
from contextlib import contextmanager
from pathlib import Path
from Functions import json_tools

class DataBase:
    def __init__(self) -> None:
        self.PATH_DataSets = str(Path(__file__).parent / 'Datasets')
        self.config = {
            'user': 'root',
            'password': 'Lu1zM1gu3l#My$QL',
            'host': 'localhost',
            'cursorclass': pymysql.cursors.DictCursor,
            'charset': 'utf8mb4'
        }
        self.create_DB()

    def create_DB(self):
        with self.connect_LocalHost() as conn:
            with conn.cursor() as cursor:
                schema_DBs = json_tools.get_schema(self.PATH_DataSets + "/Databases.json")
                cursor.execute("SHOW DATABASES")
                existing_db = cursor.fetchall()
                for db_name, tables in schema_DBs.items():
                    if not db_name in existing_db:
                        sql = f"CREATE DATABASE IF NOT EXISTS {db_name}"
                        cursor.execute(sql)
                        self.create_Tables_in_DB(db_name, tables)
    def create_Tables_in_DB(self, db_name:str, tables:dict):
        with self.connect_DB(db_name) as conn:
            with conn.cursor() as cursor:
                for table_name, columns_constraint in tables.items():
                    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
                    columns = columns_constraint["Columns"]
                    constraints = columns_constraint["CONSTRAINT"]
                    for column_name, type_options in columns.items():
                        sql += column_name + " " + type_options["TYPE"]
                        for option in type_options["OPTIONS"]:
                            sql += f" {option}"
                        sql += ", "
                    for type_constraint, name_columns in constraints.items():
                        sql += f"CONSTRAINT {name_columns['Name']} {type_constraint} ("
                        for column in name_columns["Columns"]:
                            sql += f"{column}, "
                        sql = sql[:-2]
                        sql += "), "
                    sql = sql[:-2]
                    sql += ");"
                    cursor.execute(sql)
                        
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
