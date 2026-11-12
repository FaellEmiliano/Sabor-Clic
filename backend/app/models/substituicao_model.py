from app.extensions import db
from app.models._crud import Crud_model


class SubstituicaoIngrediente(db.Model):
    __tablename__ = 'ingrediente_substituicao'

    id_ingrediente_original = db.Column(db.Integer, db.ForeignKey('ingrediente.id_ingrediente', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    id_ingrediente_substituto = db.Column(db.Integer, db.ForeignKey('ingrediente.id_ingrediente', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    prioridade = db.Column(db.Integer, nullable=False, server_default=db.text('1'))
    fator_conversao = db.Column(db.Numeric(10, 4), nullable=False, server_default=db.text('1.0000'))

    # Mantém as mesmas restrições declaradas no esquema SQL.
    __table_args__ = (
        db.CheckConstraint('fator_conversao > 0', name='chk_substituicao_fator'),
        db.CheckConstraint('prioridade > 0', name='chk_substituicao_prioridade'),
    )


class Substituicao_model(Crud_model): # Controla somente os acessos dessa entidade ao banco de dados.
    entidade = SubstituicaoIngrediente
    campos_atualizaveis = ['prioridade','fator_conversao']

    @classmethod
    def inserir_substituicao(cls, id_ingrediente_original, id_ingrediente_substituto, prioridade=1, fator_conversao=1, *, confirmar=True): # Insere um novo registro no banco.
        registro = SubstituicaoIngrediente(
            id_ingrediente_original=id_ingrediente_original,
            id_ingrediente_substituto=id_ingrediente_substituto,
            prioridade=prioridade,
            fator_conversao=fator_conversao,
        )
        return cls._inserir(registro, confirmar)

    @classmethod
    def obter_substituicao(cls, id_ingrediente_original, id_ingrediente_substituto): # Retorna o registro pela chave primária, ou None se não existir.
        return cls._obter((id_ingrediente_original, id_ingrediente_substituto))

    @classmethod
    def obter_todos(cls, **filtros): # Lista registros, permitindo filtros pelas colunas da tabela.
        return cls._listar(filtros)

    @classmethod
    def atualizar_substituicao(cls, id_ingrediente_original, id_ingrediente_substituto, *, confirmar=True, **campos): # Atualiza os campos permitidos sem modificar a chave primária.
        return cls._atualizar((id_ingrediente_original, id_ingrediente_substituto), campos, confirmar)

    @classmethod
    def deletar_substituicao(cls, id_ingrediente_original, id_ingrediente_substituto, *, confirmar=True): # Exclui o registro; vínculos são tratados pelas FKs do banco.
        return cls._deletar((id_ingrediente_original, id_ingrediente_substituto), confirmar)
