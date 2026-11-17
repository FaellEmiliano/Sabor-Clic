from app.extensions import db
from app.models._crud import Crud_model


# Representa no Python os dados de uma linha desta tabela.
# Compra em uma sessão, com estado de preparo, valor, entrega e identificador de reenvio.
class Pedido(db.Model):
    __tablename__ = 'pedido'

    id_pedido = db.Column(db.Integer, primary_key=True)
    id_sessao = db.Column(db.Integer, db.ForeignKey('sessao.id_sessao', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.text('0.00'))
    tempo_estimado = db.Column(db.Integer)
    endereco_entrega = db.Column(db.String(255))
    chave_idempotencia = db.Column(db.String(64))
    hash_requisicao = db.Column(db.String(64))
    observacoes = db.Column(db.String(500))
    preparo_em = db.Column(db.DateTime)
    pronto_em = db.Column(db.DateTime)
    entregue_em = db.Column(db.DateTime)
    cancelado_em = db.Column(db.DateTime)
    __table_args__ = (
        db.UniqueConstraint('id_sessao', 'chave_idempotencia', name='uq_pedido_idempotencia'),
        db.CheckConstraint('valor_total >= 0', name='chk_pedido_valor'),
        db.CheckConstraint('tempo_estimado IS NULL OR tempo_estimado >= 0', name='chk_pedido_tempo'),
    )
    criado_em = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())


class Pedido_model(Crud_model): # Controla somente os acessos dessa entidade ao banco de dados.
    entidade = Pedido
    campos_atualizaveis = ['status','valor_total','tempo_estimado','endereco_entrega']

    @classmethod
    # Cadastra pedido com sessão, estado, valor e dados opcionais de prazo e entrega.
    # Devolve o registro criado.
    def inserir_pedido(cls, id_sessao, status, valor_total=0.0, tempo_estimado=None, endereco_entrega=None, *, confirmar=True): # Insere um novo registro no banco.
        registro = Pedido(
            id_sessao=id_sessao,
            status=status,
            valor_total=valor_total,
            tempo_estimado=tempo_estimado,
            endereco_entrega=endereco_entrega,
        )
        return cls._inserir(registro, confirmar)

    @classmethod
    # Busca pedido pela identificação informada. Devolve None quando o registro não
    # existe.
    def obter_pedido(cls, id_pedido): # Retorna o registro pela chave primária, ou None se não existir.
        return cls._obter(id_pedido)

    @classmethod
    # Lista os registros em ordem de identificação. Os filtros opcionais usam os campos
    # da tabela.
    def obter_todos(cls, **filtros): # Lista registros, permitindo filtros pelas colunas da tabela.
        return cls._listar(filtros)

    @classmethod
    # Aplica os campos permitidos ao registro identificado e devolve o resultado. Devolve
    # None quando ele não existe.
    def atualizar_pedido(cls, id_pedido, *, confirmar=True, **campos): # Atualiza os campos permitidos sem modificar a chave primária.
        return cls._atualizar(id_pedido, campos, confirmar)

    @classmethod
    # Tenta remover o registro identificado. Devolve True se ele foi removido ou False se
    # já estava ausente.
    def deletar_pedido(cls, id_pedido, *, confirmar=True): # Exclui o registro; vínculos são tratados pelas FKs do banco.
        return cls._deletar(id_pedido, confirmar)
