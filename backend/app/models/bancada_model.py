from app.extensions import db
from app.models._crud import Crud_model


class Bancada(db.Model):
    __tablename__ = 'bancada'

    id_bancada = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    valor_hora = db.Column(db.Numeric(10, 2), nullable=False)
    ativa = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))

    __table_args__ = (db.CheckConstraint('valor_hora >= 0', name='chk_bancada_valor'),)


class Bancada_model(Crud_model): # Controla somente os acessos dessa entidade ao banco de dados.
    entidade = Bancada
    campos_atualizaveis = ['nome','descricao','valor_hora','ativa']

    @classmethod
    def inserir_bancada(cls, nome, valor_hora, descricao=None, ativa=True, *, confirmar=True): # Insere um novo registro no banco.
        registro = Bancada(
            nome=nome,
            valor_hora=valor_hora,
            descricao=descricao,
            ativa=ativa,
        )
        return cls._inserir(registro, confirmar)

    @classmethod
    def obter_bancada(cls, id_bancada): # Retorna o registro pela chave primária, ou None se não existir.
        return cls._obter(id_bancada)

    @classmethod
    def obter_todos(cls, **filtros): # Lista registros, permitindo filtros pelas colunas da tabela.
        return cls._listar(filtros)

    @classmethod
    def atualizar_bancada(cls, id_bancada, *, confirmar=True, **campos): # Atualiza os campos permitidos sem modificar a chave primária.
        return cls._atualizar(id_bancada, campos, confirmar)

    @classmethod
    def deletar_bancada(cls, id_bancada, *, confirmar=True): # Exclui o registro; vínculos são tratados pelas FKs do banco.
        return cls._deletar(id_bancada, confirmar)
