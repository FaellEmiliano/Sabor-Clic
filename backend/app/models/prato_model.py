from app.extensions import db
from app.models._crud import Crud_model


class Prato(db.Model):
    __tablename__ = 'prato'

    id_prato = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(255))
    imagem = db.Column(db.String(255))
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))

    __table_args__ = (db.CheckConstraint('preco >= 0', name='chk_prato_valor'),)


class Prato_model(Crud_model): # Controla somente os acessos dessa entidade ao banco de dados.
    entidade = Prato
    campos_atualizaveis = ['nome','descricao','preco','ativo','imagem']

    @classmethod
    def inserir_prato(cls, nome, preco, descricao=None, ativo=True, *, confirmar=True): # Insere um novo registro no banco.
        registro = Prato(
            nome=nome,
            preco=preco,
            descricao=descricao,
            ativo=ativo,
        )
        return cls._inserir(registro, confirmar)

    @classmethod
    def obter_prato(cls, id_prato): # Retorna o registro pela chave primária, ou None se não existir.
        return cls._obter(id_prato)

    @classmethod
    def obter_todos(cls, **filtros): # Lista registros, permitindo filtros pelas colunas da tabela.
        return cls._listar(filtros)

    @classmethod
    def atualizar_prato(cls, id_prato, *, confirmar=True, **campos): # Atualiza os campos permitidos sem modificar a chave primária.
        return cls._atualizar(id_prato, campos, confirmar)

    @classmethod
    def deletar_prato(cls, id_prato, *, confirmar=True): # Exclui o registro; vínculos são tratados pelas FKs do banco.
        return cls._deletar(id_prato, confirmar)
