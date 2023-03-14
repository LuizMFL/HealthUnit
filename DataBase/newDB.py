import mysql.connector
from pathlib import Path


class DataBase:
    def __init__(self) -> None:
        self.PATH_DataSets = str(Path(__file__).parent / "Datasets")
        self.mydb = mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Lu1zM1gu3l#My$QL"
        )
        self.mydb.cursor
        print(self.mydb)


if __name__ == "__main__":
    db = DataBase()
