from app.extensions import db
from app.models._crud import Crud_model


# Representa no Python os dados de uma linha desta tabela.
# Período contratado por um cliente para usar uma bancada específica.
class Reserva(db.Model):
    __tablename__ = 'reserva'

    id_reserva = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_usuario', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    id_bancada = db.Column(db.Integer, db.ForeignKey('bancada.id_bancada', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    inicio = db.Column(db.DateTime, nullable=False)
    fim = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(40), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.text('0.00'))
    criado_em = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    # Mantém as mesmas restrições declaradas no esquema SQL.
    __table_args__ = (
        db.CheckConstraint('valor_total >= 0', name='chk_reserva_valor'),
        db.CheckConstraint('fim > inicio', name='chk_reserva_periodo'),
    )


class Reserva_model(Crud_model): # Controla somente os acessos dessa entidade ao banco de dados.
    entidade = Reserva
    campos_atualizaveis = ['id_cliente','id_bancada','inicio','fim','status','valor_total']

    @classmethod
    # Cadastra reserva com cliente, bancada, horários, estado e preço total. Devolve o
    # registro criado.
    def inserir_reserva(cls, id_cliente, id_bancada, inicio, fim, status, valor_total=0.0, *, confirmar=True): # Insere um novo registro no banco.
        registro = Reserva(
            id_cliente=id_cliente,
            id_bancada=id_bancada,
            inicio=inicio,
            fim=fim,
            status=status,
            valor_total=valor_total,
        )
        return cls._inserir(registro, confirmar)

    @classmethod
    # Busca reserva pela identificação informada. Devolve None quando o registro não
    # existe.
    def obter_reserva(cls, id_reserva): # Retorna o registro pela chave primária, ou None se não existir.
        return cls._obter(id_reserva)

    @classmethod
    # Lista os registros em ordem de identificação. Os filtros opcionais usam os campos
    # da tabela.
    def obter_todos(cls, **filtros): # Lista registros, permitindo filtros pelas colunas da tabela.
        return cls._listar(filtros)

    @classmethod
    # Aplica os campos permitidos ao registro identificado e devolve o resultado. Devolve
    # None quando ele não existe.
    def atualizar_reserva(cls, id_reserva, *, confirmar=True, **campos): # Atualiza os campos permitidos sem modificar a chave primária.
        return cls._atualizar(id_reserva, campos, confirmar)

    @classmethod
    # Tenta remover o registro identificado. Devolve True se ele foi removido ou False se
    # já estava ausente.
    def deletar_reserva(cls, id_reserva, *, confirmar=True): # Exclui o registro; vínculos são tratados pelas FKs do banco.
        return cls._deletar(id_reserva, confirmar)
