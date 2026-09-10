import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.model.database import Database

class Usuario_model:
    @staticmethod
    def criar_tabela():
        try:
            conn = Database.conectar()
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS usuario(
                        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        email TEXT NOT NULL,
                        ativo INTEGER DEFAULT 1,
                        senha_hash TEXT NOT NULL
                        )''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f'ERROR: {e}')
            conn.rollback()
            conn.close()
    @staticmethod
    def inserir_usuario(nome, email, senha):
        try:
            conn = Database.conectar()
            cursor = conn.cursor()
            senha_hash = generate_password_hash(senha)
            cursor.execute('INSERT INTO usuarios(nome, email, senha_hash) VALUES(?, ?, ?)', (nome, email, senha_hash))
        except sqlite3.Error as e:
            print(f'ERROR: {e}')
            conn.rollback()
            conn.close()
    @staticmethod
    def pegar_usuario(id):
        try:
            conn = Database.conectar()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE id = ?', (id,))
            user = cursor.fetchone()
            return user
        except sqlite3.Error as e:
            print(f'ERROR: {e}')
            conn.rollback()
            conn.close()

    @staticmethod
    def atualizar_usuario(nome, email, senha):
        pass # eu vou voltar aqui dps


