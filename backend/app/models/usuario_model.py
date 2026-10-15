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
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    senha_hash = db.Column(db.String(256), nullable=False)

    # Essa coluna dita de qual especialidade é esse usuário.
    tipo = db.Column(db.String(256))

    __mapper_args__ = { # Diz ao SQLAlchemy qual especialidade ele deve ter em mente quando criar o novo registro
        'polymorphic_identity': 'usuario',
        'polymorphic_on': tipo
    }

    def __init__(self, nome, email, senha, ativo=True): # isso é só pro pylance parar de chorar.
        self.nome = nome
        self.email = email
        self.senha_hash = generate_password_hash(senha)
        self.ativo = ativo

class Cozinheiro(Usuario): # Criando a tabela de Cozinheiro, que é uma especialidade de Usuario.
    __tablename__ = 'cozinheiro'

    __mapper_args__ = {
        'polymorphic_identity': 'cozinheiro'
    }

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), primary_key=True)
    turno = db.Column(db.String(50), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    def __init__(self, nome, email, senha, turno, especialidade, ativo=True):
        super().__init__(nome, email, senha, ativo)
        self.turno = turno
        self.especialidade = especialidade

class Cliente(Usuario): # Criando a tabela de Cliente, que é uma especialidade Usuario.
    __tablename__ = 'cliente'

    __mapper_args__ = {
        'polymorphic_identity': 'cliente'
    }

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), primary_key=True)
    endereco_entrega = db.Column(db.String(256))
    def __init__(self, nome, email, senha, endereco_entrega, ativo=True):
        super().__init__(nome, email, senha, ativo)
        self.endereco_entrega = endereco_entrega

class Administrador(Usuario): # Criando a tabela de Administrador, que é uma especialidade de Usuario.
    __tablename__ = 'administrador'

    __mapper_args__ = {
        'polymorphic_identity': 'administrador'
    }

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), primary_key=True)

class Usuario_model: # Classe pra controlar os acessos ao banco de dados
    @staticmethod
    def inserir_cozinheiro(nome, email, senha, turno, especialidade, ativo=True): # Insere um novo cozinheiro no banco de dados.
        novo_cozinheiro = Cozinheiro(nome, email, senha, turno, especialidade, ativo)
        db.session.add(novo_cozinheiro)
        db.session.commit()
        return novo_cozinheiro

    @staticmethod
    def inserir_cliente(nome, email, senha, endereco_entrega, ativo=True): # Insere um novo cozinheiro no banco de dados.
        novo_cliente = Cliente(nome, email, senha, endereco_entrega, ativo)
        db.session.add(novo_cliente)
        db.session.commit()
        return novo_cliente

    @staticmethod
    def inserir_administrador(nome, email, senha, ativo=True):
        novo_admin = Administrador(nome, email, senha, ativo)
        db.session.add(novo_admin)
        db.session.commit()
        return novo_admin

    @staticmethod
    def obter_usuario_id(id_usuario): # Retorna um usuario a partir do ID especificado.
        return db.session.get(Usuario, id_usuario)

    @staticmethod
    def obter_cozinheiro_id(id_cozinheiro): # Retorna um cozinheiro a partir do ID especificado. O do usuário já faz isso automáticamente, mas ainda é bom ter separado para as regras de négocio.
        return db.session.get(Cozinheiro, id_cozinheiro)

    @staticmethod
    def obter_cliente_id(id_cliente): # Retorna um cliente pelo ID especificado.
        return db.session.get(Cliente, id_cliente)

    @staticmethod
    def obter_usuario_email(email): # Retorna um usuario a partir do email especificado.
        return Usuario.query.filter_by(email=email).first()

    @staticmethod
    def obter_todos(): # Retorna todos os usuários do banco.
        return Usuario.query.all()

    @staticmethod
    def atualizar_usuario(id_usuario, **kwargs): # Atualiza os dados do Usuario. Os dados atualizados dependem dos argumentos dados.
        usuario = Usuario_model.obter_usuario_id(id_usuario)
        if not usuario:
            return None

        for campo, novo_valor in kwargs.items():
            if hasattr(usuario, campo):
                if campo not in ['id_usuario', 'senha_hash', 'ativo', 'email']:
                    setattr(usuario, campo, novo_valor)
                else:
                    match campo:
                        case 'senha_hash':
                            if check_password_hash(usuario.senha_hash, novo_valor):
                                return False
                            setattr(usuario, 'senha_hash', generate_password_hash(novo_valor))

                        case 'email':
                            if Usuario_model.obter_usuario_email(novo_valor):
                                return False
                            setattr(usuario, 'email', novo_valor)
        db.session.commit()
        return usuario

    @staticmethod
    def mudar_atividade(id_usuario): # Muda o status de um usuario.
        usuario = Usuario_model.obter_usuario_id(id_usuario)
        if not usuario:
            return False
        usuario.ativo = not usuario.ativo
        db.session.commit()
        return True

    @staticmethod
    def deletar_usuario(id_usuario):
        usuario = Usuario_model.obter_usuario_id(id_usuario)
        if not usuario:
            return False
        try:
            db.session.delete(usuario)
            db.session.commit()
            return True
        except Exception as e: # Se der qualquer erro no banco o rollback desfaz a operação e impede o travamento do banco.
            db.session.rollback()
            return False
        

    