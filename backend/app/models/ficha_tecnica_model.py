from app.extensions import db
from app.models._crud import Crud_model


# Representa no Python os dados de uma linha desta tabela.
# Relação entre um prato e um ingrediente, com a quantidade por unidade da receita.
class FichaTecnica(db.Model):
    __tablename__ = 'ficha_tecnica'

    id_prato = db.Column(db.Integer, db.ForeignKey('prato.id_prato', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id_ingrediente', ondelete='RESTRICT', onupdate='CASCADE'), primary_key=True)
    quantidade_necessaria = db.Column(db.Numeric(12, 3), nullable=False)

    # Mantém as mesmas restrições declaradas no esquema SQL.
    __table_args__ = (
        db.CheckConstraint('quantidade_necessaria > 0', name='chk_ficha_quantidade'),
    )


class FichaTecnica_model(Crud_model): # Controla somente os acessos dessa entidade ao banco de dados.
    entidade = FichaTecnica
    campos_atualizaveis = ['quantidade_necessaria']

    @classmethod
    # Cadastra ficha técnica com números do prato e do ingrediente e quantidade da
    # receita. Devolve o registro criado.
    def inserir_ficha_tecnica(cls, id_prato, id_ingrediente, quantidade_necessaria, *, confirmar=True): # Insere um novo registro no banco.
        registro = FichaTecnica(
            id_prato=id_prato,
            id_ingrediente=id_ingrediente,
            quantidade_necessaria=quantidade_necessaria,
        )
        return cls._inserir(registro, confirmar)

    @classmethod
    # Busca ficha técnica pela identificação informada. Devolve None quando o registro
    # não existe.
    def obter_ficha_tecnica(cls, id_prato, id_ingrediente): # Retorna o registro pela chave primária, ou None se não existir.
        return cls._obter((id_prato, id_ingrediente))

    @classmethod
    # Lista os registros em ordem de identificação. Os filtros opcionais usam os campos
    # da tabela.
    def obter_todos(cls, **filtros): # Lista registros, permitindo filtros pelas colunas da tabela.
        return cls._listar(filtros)

    @classmethod
    # Aplica os campos permitidos ao registro identificado e devolve o resultado. Devolve
    # None quando ele não existe.
    def atualizar_ficha_tecnica(cls, id_prato, id_ingrediente, *, confirmar=True, **campos): # Atualiza os campos permitidos sem modificar a chave primária.
        return cls._atualizar((id_prato, id_ingrediente), campos, confirmar)

    @classmethod
    # Tenta remover o registro identificado. Devolve True se ele foi removido ou False se
    # já estava ausente.
    def deletar_ficha_tecnica(cls, id_prato, id_ingrediente, *, confirmar=True): # Exclui o registro; vínculos são tratados pelas FKs do banco.
        return cls._deletar((id_prato, id_ingrediente), confirmar)
