from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models._crud import Crud_model, salvar_alteracoes


class Usuario(db.Model): # Mapeia os dados comuns exatamente como estão na tabela usuario.
    __tablename__ = 'usuario'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    senha_hash = db.Column(db.String(255), nullable=False)

    # O esquema usa tabelas especializadas, sem uma coluna tipo na tabela usuario.
    cliente = db.relationship('Cliente', back_populates='usuario', uselist=False, passive_deletes='all')
    cozinheiro = db.relationship('Cozinheiro', back_populates='usuario', uselist=False, passive_deletes='all')
    administrador = db.relationship('Administrador', back_populates='usuario', uselist=False, passive_deletes='all')

    def __init__(self, nome, email, senha, ativo=True): # Protege a senha antes de preparar o registro.
        self.nome = nome
        self.email = email
        self.senha_hash = generate_password_hash(senha)
        self.ativo = ativo


class Cliente(db.Model): # Guarda os dados exclusivos do cliente e referencia o usuário correspondente.
    __tablename__ = 'cliente'

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, autoincrement=False)
    endereco_entrega = db.Column(db.String(255))
    usuario = db.relationship('Usuario', back_populates='cliente')


class Cozinheiro(db.Model): # Guarda os dados exclusivos do cozinheiro, conforme o esquema SQL.
    __tablename__ = 'cozinheiro'

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, autoincrement=False)
    turno = db.Column(db.String(50))
    especialidade = db.Column(db.String(100))
    usuario = db.relationship('Usuario', back_populates='cozinheiro')


class Administrador(db.Model): # Identifica um administrador pelo vínculo com usuario.
    __tablename__ = 'administrador'

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, autoincrement=False)
    usuario = db.relationship('Usuario', back_populates='administrador')


class Usuario_model(Crud_model): # Classe pra controlar os acessos dos usuários ao banco de dados.
    entidade = Usuario
    campos_atualizaveis = ('nome', 'email', 'ativo')

    @classmethod
    def inserir_usuario(cls, nome, email, senha, ativo=True, *, confirmar=True): # Insere somente os dados comuns do usuário.
        return cls._inserir(Usuario(nome, email, senha, ativo), confirmar)

    @staticmethod
    def inserir_cliente(nome, email, senha, endereco_entrega=None, ativo=True, *, confirmar=True): # Insere usuário e cliente na mesma transação.
        cliente = Cliente(usuario=Usuario(nome, email, senha, ativo), endereco_entrega=endereco_entrega)
        db.session.add(cliente)
        salvar_alteracoes(confirmar)
        return cliente

    @staticmethod
    def inserir_cozinheiro(nome, email, senha, turno=None, especialidade=None, ativo=True, *, confirmar=True): # Insere usuário e cozinheiro juntos.
        cozinheiro = Cozinheiro(usuario=Usuario(nome, email, senha, ativo), turno=turno, especialidade=especialidade)
        db.session.add(cozinheiro)
        salvar_alteracoes(confirmar)
        return cozinheiro

    @staticmethod
    def inserir_administrador(nome, email, senha, ativo=True, *, confirmar=True): # Insere usuário e administrador juntos.
        administrador = Administrador(usuario=Usuario(nome, email, senha, ativo))
        db.session.add(administrador)
        salvar_alteracoes(confirmar)
        return administrador

    @classmethod
    def obter_usuario_id(cls, id_usuario): # Retorna os dados comuns pelo ID especificado.
        return cls._obter(id_usuario)

    @staticmethod
    def obter_cliente_id(id_cliente): # Retorna os dados do cliente; os dados comuns ficam em cliente.usuario.
        return db.session.get(Cliente, id_cliente)

    @staticmethod
    def obter_cozinheiro_id(id_cozinheiro): # Retorna os dados do cozinheiro e seu vínculo com usuario.
        return db.session.get(Cozinheiro, id_cozinheiro)

    @staticmethod
    def obter_administrador_id(id_administrador): # Retorna a especialização de administrador.
        return db.session.get(Administrador, id_administrador)

    @staticmethod
    def obter_usuario_email(email): # Busca um usuário pelo e-mail informado.
        return db.session.scalar(db.select(Usuario).where(Usuario.email == email))

    @classmethod
    def obter_todos(cls, **filtros): # Lista usuários, permitindo filtros pelas colunas comuns.
        return cls._listar(filtros)

    @classmethod
    def atualizar_usuario(cls, id_usuario, *, confirmar=True, **campos): # Atualiza somente nome, e-mail e atividade.
        return cls._atualizar(id_usuario, campos, confirmar)

    @staticmethod
    def atualizar_senha(id_usuario, senha, *, confirmar=True): # Recebe a nova senha e grava somente seu hash.
        usuario = db.session.get(Usuario, id_usuario)
        if usuario is None:
            return None
        usuario.senha_hash = generate_password_hash(senha)
        salvar_alteracoes(confirmar)
        return usuario

    @staticmethod
    def mudar_atividade(id_usuario, *, confirmar=True): # Alterna a atividade do usuário já cadastrado.
        usuario = db.session.get(Usuario, id_usuario)
        if usuario is None:
            return False
        usuario.ativo = not usuario.ativo
        salvar_alteracoes(confirmar)
        return True

    @classmethod
    def deletar_usuario(cls, id_usuario, *, confirmar=True): # Exclui o usuário e deixa o banco aplicar CASCADE ou RESTRICT.
        return cls._deletar(id_usuario, confirmar)


class Cliente_model(Crud_model): # Controla o cadastro especializado de clientes existentes.
    entidade = Cliente
    campos_atualizaveis = ('endereco_entrega',)

    @classmethod
    def inserir_cliente(cls, id_usuario, endereco_entrega=None, *, confirmar=True): # Vincula um usuário já cadastrado à tabela cliente.
        return cls._inserir(Cliente(id_usuario=id_usuario, endereco_entrega=endereco_entrega), confirmar)

    @classmethod
    def obter_cliente(cls, id_usuario): # Consulta o cliente pela chave compartilhada com usuario.
        return cls._obter(id_usuario)

    @classmethod
    def obter_todos(cls, **filtros): # Lista os registros especializados de clientes.
        return cls._listar(filtros)

    @classmethod
    def atualizar_cliente(cls, id_usuario, *, confirmar=True, **campos): # Atualiza o endereço sem modificar o usuário comum.
        return cls._atualizar(id_usuario, campos, confirmar)

    @classmethod
    def deletar_cliente(cls, id_usuario, *, confirmar=True): # Exclui somente a especialização; reservas podem impedir a operação.
        return cls._deletar(id_usuario, confirmar)


class Cozinheiro_model(Crud_model): # Controla os dados profissionais dos cozinheiros.
    entidade = Cozinheiro
    campos_atualizaveis = ('turno', 'especialidade')

    @classmethod
    def inserir_cozinheiro(cls, id_usuario, turno=None, especialidade=None, *, confirmar=True): # Vincula um usuário já cadastrado à tabela cozinheiro.
        return cls._inserir(Cozinheiro(id_usuario=id_usuario, turno=turno, especialidade=especialidade), confirmar)

    @classmethod
    def obter_cozinheiro(cls, id_usuario): # Consulta a especialização pelo ID do usuário.
        return cls._obter(id_usuario)

    @classmethod
    def obter_todos(cls, **filtros): # Lista cozinheiros e permite filtrar os dados profissionais.
        return cls._listar(filtros)

    @classmethod
    def atualizar_cozinheiro(cls, id_usuario, *, confirmar=True, **campos): # Atualiza turno e especialidade.
        return cls._atualizar(id_usuario, campos, confirmar)

    @classmethod
    def deletar_cozinheiro(cls, id_usuario, *, confirmar=True): # Exclui somente a especialização, preservando usuario.
        return cls._deletar(id_usuario, confirmar)


class Administrador_model(Crud_model): # Controla o vínculo de administrador de um usuário existente.
    entidade = Administrador
    campos_atualizaveis = ()

    @classmethod
    def inserir_administrador(cls, id_usuario, *, confirmar=True): # Vincula um usuário já cadastrado à tabela administrador.
        return cls._inserir(Administrador(id_usuario=id_usuario), confirmar)

    @classmethod
    def obter_administrador(cls, id_usuario): # Consulta o vínculo administrativo.
        return cls._obter(id_usuario)

    @classmethod
    def obter_todos(cls, **filtros): # Lista os administradores cadastrados.
        return cls._listar(filtros)

    @classmethod
    def deletar_administrador(cls, id_usuario, *, confirmar=True): # Remove somente o vínculo administrativo.
        return cls._deletar(id_usuario, confirmar)

    # Administrador não possui campos editáveis além da PK; os dados comuns são atualizados em Usuario_model.
