import os
import sqlite3
from contextlib import contextmanager


class Database:
    def __init__(self, db_path: str = "reports.db"):
        self.db_path = os.path.abspath(db_path)

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            yield conn
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            conn.close()


db = Database()
