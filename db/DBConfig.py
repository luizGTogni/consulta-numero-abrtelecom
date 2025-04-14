import sqlite3
import os

class DBConfig:
    def __init__(self, name_db):
        self.name_db = name_db
        self.conn = sqlite3.connect(os.path.join('..', f'{name_db}.db')) 
        self.cursor = self.conn.cursor()

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS consults (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                provider_name TEXT NOT NULL,
                date_recent TEXT,
                number_months INTEGER,
                message TEXT NOT NULL
            )
        """)

        self.conn.commit()

    def close(self):
        return self.conn.close()