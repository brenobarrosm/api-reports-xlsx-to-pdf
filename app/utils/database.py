import os
import sqlite3


class Database:
    def __init__(self, db_path: str = "reports.db"):
        self.db_path = os.path.abspath(db_path)
        self.connection = None
        self._connect()

    def _connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            print(f"[INFO] Conectado ao banco de dados em: {self.db_path}")
        except sqlite3.Error as e:
            print(f"[ERROR] Falha ao conectar no banco de dados: {e}")

    def get_connection(self):
        return self.connection

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("[INFO] Conexão com banco de dados encerrada.")


db = Database()
