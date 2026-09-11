import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.model.database import Database

class Usuario_model:
    @staticmethod
    def criar_tabela():
        try:
            conn = Database.conectar()
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios(
                        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
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
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f'ERROR: {e}')
            conn.rollback()
            conn.close()
    @staticmethod
    def pegar_usuario(id):
        try:
            conn = Database.conectar()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE id_usuario = ?', (id,))
            usuario = cursor.fetchone()
            conn.close
            if not usuario:
                return None
            return usuario
        except sqlite3.Error as e:
            print(f'ERROR: {e}')
            conn.rollback()
            conn.close()

    @staticmethod
    def autenticar_usuario(email, senha):
        try:
            conn = Database.conectar()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
            usuario = cursor.fetchone()
            conn.close()
            if usuario:
                hash_do_banco = usuario['senha_hash']
                if check_password_hash(hash_do_banco, senha):
                    return True, usuario['id_usuario']
            return False, None
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f'ERRO: {e}')
            return False, None

    @staticmethod
    def verificar_email_existente(email):
        try:
            conn = Database.conectar()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
            usuario = cursor.fetchone()
            if not usuario:
                return False
            return True
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f'ERRO: {e}')
            return False

    @staticmethod
    def deletar_usuario(id):
        try:
            conn = Database.conectar()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM usuarios WHERE id_usuario = ?', (id,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f'ERRO: {e}')

    @staticmethod
    def atualizar_usuario(id, nome, email, senha):
        try:
            conn = Database.conectar()
            cursor = conn.cursor()
            if nome:
                cursor.execute('UPDATE usuarios SET nome = ? WHERE id_usuario = ?', (nome, id))
            if email:
                cursor.execute('UPDATE usuarios SET email = ? WHERE id_usuario = ?', (email, id))
            if senha:
                senha_hash = generate_password_hash(senha)
                cursor.execute('UPDATE usuarios SET senha_hash = ? WHERE id_usuario = ?', (senha_hash, id))
            conn.close()
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f'ERRO: {e}')
