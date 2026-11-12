from app.extensions import db
from app.models._crud import Crud_model


class ItemPedido(db.Model):
    __tablename__ = 'item_pedido'

    id_item_pedido = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedido.id_pedido', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_prato = db.Column(db.Integer, db.ForeignKey('prato.id_prato', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    nome_prato = db.Column(db.String(120))
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    # Mantém as mesmas restrições declaradas no esquema SQL.
    __table_args__ = (
        db.CheckConstraint('preco_unitario >= 0 AND subtotal >= 0', name='chk_item_valores'),
        db.CheckConstraint('quantidade > 0', name='chk_item_pedido_quantidade'),
    )


class ItemPedido_model(Crud_model): # Controla somente os acessos dessa entidade ao banco de dados.
    entidade = ItemPedido
    campos_atualizaveis = ['id_prato','quantidade','preco_unitario','subtotal']

    @classmethod
    def inserir_item_pedido(cls, id_pedido, id_prato, quantidade, preco_unitario, subtotal, *, confirmar=True): # Insere um novo registro no banco.
        registro = ItemPedido(
            id_pedido=id_pedido,
            id_prato=id_prato,
            quantidade=quantidade,
            preco_unitario=preco_unitario,
            subtotal=subtotal,
        )
        return cls._inserir(registro, confirmar)

    @classmethod
    def obter_item_pedido(cls, id_item_pedido): # Retorna o registro pela chave primária, ou None se não existir.
        return cls._obter(id_item_pedido)

    @classmethod
    def obter_todos(cls, **filtros): # Lista registros, permitindo filtros pelas colunas da tabela.
        return cls._listar(filtros)

    @classmethod
    def atualizar_item_pedido(cls, id_item_pedido, *, confirmar=True, **campos): # Atualiza os campos permitidos sem modificar a chave primária.
        return cls._atualizar(id_item_pedido, campos, confirmar)

    @classmethod
    def deletar_item_pedido(cls, id_item_pedido, *, confirmar=True): # Exclui o registro; vínculos são tratados pelas FKs do banco.
        return cls._deletar(id_item_pedido, confirmar)
