import sqlite3
from config import Config

class Database:
    @staticmethod
    def conectar():
        conn = sqlite3.connect(Config.DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
