'''from copy import deepcopy


class UsuarioModel:
    _originais = [
        {"id": 1, "nome": "Rafael Gomes", "email": "rafael@exemplo.com", "perfil": "cliente"},
        {"id": 2, "nome": "Marina Souza", "email": "marina@saboreclic.com", "perfil": "cozinha"},
        {"id": 3, "nome": "Ana Martins", "email": "ana@saboreclic.com", "perfil": "admin"},
    ]
    _usuarios = deepcopy(_originais)

    @classmethod
    def reiniciar(cls):
        cls._usuarios = deepcopy(cls._originais)

    @classmethod
    def obter(cls, id_usuario):
        usuario = next((item for item in cls._usuarios if item["id"] == id_usuario), None)
        return deepcopy(usuario)

    @classmethod
    def obter_por_email(cls, email):
        email_normalizado = email.strip().lower()
        usuario = next(
            (item for item in cls._usuarios if item["email"].lower() == email_normalizado),
            None,
        )
        return deepcopy(usuario)

    @classmethod
    def criar(cls, nome, email, perfil):
        usuario = {
            "id": max((item["id"] for item in cls._usuarios), default=0) + 1,
            "nome": nome,
            "email": email.strip().lower(),
            "perfil": perfil,
        }
        cls._usuarios.append(usuario)
        return deepcopy(usuario)'''

from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model): # Criando o modelo da entidade Usuario, seguindo a base do MER do projeto.
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    senha_hash = db.Column(db.String(256), nullable=False)

    def __init__(self, nome, email, senha, ativo=True):
        self.nome = nome
        self.email = email
        self.senha_hash = generate_password_hash(senha)
        self.ativo = ativo
class Usuario_model:
    @staticmethod
    def insert_user(nome, email, senha, ativo=True):
        novo_usuario = Usuario(nome, email, senha, ativo)
