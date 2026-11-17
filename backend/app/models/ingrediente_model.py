from app.extensions import db
from app.models._crud import Crud_model


# Representa no Python os dados de uma linha desta tabela.
# Insumo da cozinha, medido na unidade cadastrada e com saldo próprio.
class Ingrediente(db.Model):
    __tablename__ = 'ingrediente'

    id_ingrediente = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    imagem = db.Column(db.String(255))
    unidade_medida = db.Column(db.String(30), nullable=False)
    quantidade_estoque = db.Column(db.Numeric(12, 3), nullable=False, server_default=db.text('0.000'))

    __table_args__ = (db.CheckConstraint('quantidade_estoque >= 0', name='chk_ingrediente_valor'),)


class Ingrediente_model(Crud_model): # Controla somente os acessos dessa entidade ao banco de dados.
    entidade = Ingrediente
    campos_atualizaveis = ['nome','unidade_medida','quantidade_estoque','imagem']

    @classmethod
    # Cadastra ingrediente com nome, unidade e saldo inicial. Devolve o registro criado.
    def inserir_ingrediente(cls, nome, unidade_medida, quantidade_estoque=0, *, confirmar=True): # Insere um novo registro no banco.
        registro = Ingrediente(
            nome=nome,
            unidade_medida=unidade_medida,
            quantidade_estoque=quantidade_estoque,
        )
        return cls._inserir(registro, confirmar)

    @classmethod
    # Busca ingrediente pela identificação informada. Devolve None quando o registro não
    # existe.
    def obter_ingrediente(cls, id_ingrediente): # Retorna o registro pela chave primária, ou None se não existir.
        return cls._obter(id_ingrediente)

    @classmethod
    # Lista os registros em ordem de identificação. Os filtros opcionais usam os campos
    # da tabela.
    def obter_todos(cls, **filtros): # Lista registros, permitindo filtros pelas colunas da tabela.
        return cls._listar(filtros)

    @classmethod
    # Aplica os campos permitidos ao registro identificado e devolve o resultado. Devolve
    # None quando ele não existe.
    def atualizar_ingrediente(cls, id_ingrediente, *, confirmar=True, **campos): # Atualiza os campos permitidos sem modificar a chave primária.
        return cls._atualizar(id_ingrediente, campos, confirmar)

    @classmethod
    # Tenta remover o registro identificado. Devolve True se ele foi removido ou False se
    # já estava ausente.
    def deletar_ingrediente(cls, id_ingrediente, *, confirmar=True): # Exclui o registro; vínculos são tratados pelas FKs do banco.
        return cls._deletar(id_ingrediente, confirmar)
