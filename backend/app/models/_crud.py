from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db


# Com confirmar=True, torna as mudanças definitivas. Com False, envia as mudanças ao banco
# para poder confirmar várias juntas mais tarde. Se houver falha, descarta a operação inteira.
def salvar_alteracoes(confirmar=True): # Confirma a operação ou envia o SQL sem encerrar a transação.
    try:
        if confirmar:
            db.session.commit()
        else:
            # Permite que várias operações sejam confirmadas juntas pelo chamador.
            db.session.flush()
    except SQLAlchemyError:
        # Desfaz a transação inteira e mantém o erro disponível para quem chamou.
        db.session.rollback()
        raise


# Implementação compartilhada usada pelos cadastros para gravar e consultar registros.
class Crud_model: # Reúne somente as operações de persistência compartilhadas pelos models.
    entidade = None
    campos_atualizaveis = ()

    @classmethod
    def _inserir(cls, registro, confirmar=True): # Insere uma entidade e retorna o objeto persistido.
        db.session.add(registro)
        salvar_alteracoes(confirmar)
        return registro

    @classmethod
    def _obter(cls, chave): # Aceita uma chave simples ou uma tupla para as tabelas associativas.
        return db.session.get(cls.entidade, chave)

    @classmethod
    # Recusa filtros que não correspondem à tabela antes de executar a busca.
    def _listar(cls, filtros): # Filtra apenas pelas colunas reais e ordena pela chave primária.
        colunas = cls.entidade.__table__.columns
        desconhecidos = set(filtros) - set(colunas.keys())
        if desconhecidos:
            raise ValueError(f"Filtros não permitidos: {', '.join(sorted(desconhecidos))}.")
        consulta = db.select(cls.entidade).filter_by(**filtros).order_by(*cls.entidade.__table__.primary_key.columns)
        return list(db.session.scalars(consulta).all())

    @classmethod
    # Confere se todos os campos podem mudar antes de editar o registro.
    # Quando a identificação não existe, devolve None.
    def _atualizar(cls, chave, campos, confirmar=True): # Atualiza somente as colunas liberadas pelo model.
        desconhecidos = set(campos) - set(cls.campos_atualizaveis)
        if desconhecidos:
            raise ValueError(f"Campos não permitidos: {', '.join(sorted(desconhecidos))}.")
        registro = cls._obter(chave)
        if registro is None:
            return None
        for campo, valor in campos.items():
            setattr(registro, campo, valor)
        salvar_alteracoes(confirmar)
        return registro

    @classmethod
    # Devolve False se não houver registro e True se a exclusão foi solicitada ao banco.
    def _deletar(cls, chave, confirmar=True): # Exclui o registro respeitando as restrições do banco.
        registro = cls._obter(chave)
        if registro is None:
            return False
        db.session.delete(registro)
        salvar_alteracoes(confirmar)
        return True
