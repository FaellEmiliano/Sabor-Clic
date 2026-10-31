# Importa o tratamento de erros do SQLAlchemy para evitar travamento da API por quebra de constraints
from sqlalchemy.exc import SQLAlchemyError

# Importa o model que gerencia o acesso à tabela sessao[cite: 12]
from app.models.sessao_model import Sessao_model

class SessaoController:
    """Controlador que concentra as regras de negócio relacionadas às sessões das bancadas."""

    @staticmethod
    def _serializar_sessao(sessao):
        """
        Método auxiliar (DRY) para converter a entidade SQLAlchemy 'Sessao' em dicionário.
        Formata adequadamente os objetos DateTime para String ISO 8601, permitindo o retorno JSON.
        """
        return {
            "id_sessao": sessao.id_sessao,
            "id_reserva": sessao.id_reserva,
            "codigo_acesso": sessao.codigo_acesso,
            "status": sessao.status,
            # Serializa os campos de data de forma segura, verificando se não são nulos[cite: 12]
            "criado_em": sessao.criado_em.isoformat() if sessao.criado_em else None,
            "iniciado_em": sessao.iniciado_em.isoformat() if sessao.iniciado_em else None,
            "encerrado_em": sessao.encerrado_em.isoformat() if sessao.encerrado_em else None
        }

    @staticmethod
    def criar(id_reserva, codigo_acesso, status, iniciado_em=None, encerrado_em=None):
        """
        Valida e cadastra uma nova sessão.
        Campos obrigatórios: id_reserva, codigo_acesso, status[cite: 12].
        """
        # Checagem rigorosa da presença dos campos NOT NULL exigidos pelo banco de dados
        if not id_reserva or not codigo_acesso or not status:
            return {"erro": "Os campos 'id_reserva', 'codigo_acesso' e 'status' são obrigatórios."}, 400

        try:
            # Envia os dados convertidos e tipados conforme assinatura do model[cite: 12]
            # O SQLAlchemy se encarrega de converter strings ISO válidas em DateTime para iniciado_em e encerrado_em
            nova_sessao = Sessao_model.inserir_sessao(
                id_reserva=int(id_reserva),
                codigo_acesso=str(codigo_acesso),
                status=str(status),
                iniciado_em=iniciado_em,
                encerrado_em=encerrado_em
            )
            return {
                "mensagem": "Sessão criada com sucesso.",
                "sessao": SessaoController._serializar_sessao(nova_sessao)
            }, 201
        except SQLAlchemyError:
            # Captura a violação das restrições UNIQUE para 'id_reserva' e 'codigo_acesso'[cite: 12]
            return {"erro": "Erro ao criar a sessão. Verifique se o código de acesso ou a reserva já estão em uso."}, 409

    @staticmethod
    def obter_por_id(id_sessao):
        """Busca os dados de uma sessão específica pela chave primária[cite: 12]."""
        sessao = Sessao_model.obter_sessao(id_sessao)
        if not sessao:
            return {"erro": "Sessão não encontrada."}, 404

        return {"sessao": SessaoController._serializar_sessao(sessao)}, 200

    @staticmethod
    def obter_todos(filtros=None):
        """
        Lista as sessões cadastradas. 
        Permite aplicar filtros (ex: listar todas com status='ativa' ou buscar por codigo_acesso)[cite: 12].
        """
        filtros = filtros or {}
        try:
            sessoes = Sessao_model.obter_todos(**filtros)
            return {"sessoes": [SessaoController._serializar_sessao(s) for s in sessoes]}, 200
        except ValueError as e:
            return {"erro": str(e)}, 400

    @staticmethod
    def atualizar(id_sessao, **kwargs):
        """
        Altera as informações da sessão.
        Permitido: codigo_acesso, status, iniciado_em, encerrado_em[cite: 12].
        A chave 'id_reserva' é bloqueada nativamente pelo _crud.py por não estar nos campos_atualizaveis[cite: 12].
        """
        try:
            sessao_atualizada = Sessao_model.atualizar_sessao(id_sessao, **kwargs)
            
            if not sessao_atualizada:
                return {"erro": "Sessão não encontrada."}, 404
                
            return {
                "mensagem": "Sessão atualizada com sucesso.", 
                "sessao": SessaoController._serializar_sessao(sessao_atualizada)
            }, 200
            
        except ValueError as e:
            # Barra chaves invasoras (ex: tentativa de mudar id_reserva ou id_sessao)
            return {"erro": str(e)}, 400
        except SQLAlchemyError:
            return {"erro": "Erro ao atualizar a sessão. O código de acesso escolhido já pode estar em uso."}, 409

    @staticmethod
    def deletar(id_sessao):
        """
        Remove a sessão permanentemente. 
        Vínculos de tabelas filhas (como pedidos daquela sessão) são tratados via CASCADE no banco[cite: 12].
        """
        try:
            sucesso = Sessao_model.deletar_sessao(id_sessao)
            if not sucesso:
                return {"erro": "Sessão não encontrada."}, 404
                
            return {"mensagem": "Sessão deletada com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Erro interno ao tentar deletar a sessão."}, 500