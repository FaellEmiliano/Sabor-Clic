# Importa o tratamento de erros do banco de dados para capturar falhas de chave estrangeira e persistência
from sqlalchemy.exc import SQLAlchemyError

# Importa o model que gerencia o acesso à tabela pedido[cite: 9]
from app.models.pedido_model import Pedido_model

class PedidoController:
    """Controlador responsável por concentrar a regra de negócio dos pedidos."""

    @staticmethod
    def _serializar_pedido(pedido):
        """
        Método auxiliar (DRY) para converter a entidade SQLAlchemy em dicionário.
        Lida com a conversão de Numeric para float[cite: 9] e formata a data para string ISO 8601.
        """
        return {
            "id_pedido": pedido.id_pedido,
            "id_sessao": pedido.id_sessao,
            "status": pedido.status,
            "valor_total": float(pedido.valor_total) if pedido.valor_total is not None else 0.0,
            "tempo_estimado": int(pedido.tempo_estimado) if pedido.tempo_estimado is not None else None,
            "endereco_entrega": pedido.endereco_entrega,
            # Converte o objeto datetime em uma string padronizada (ex: '2026-10-30T20:42:00')
            "criado_em": pedido.criado_em.isoformat() if pedido.criado_em else None
        }

    @staticmethod
    def criar(id_sessao, status, valor_total=0, tempo_estimado=None, endereco_entrega=None):
        """
        Valida e cadastra um novo pedido no banco de dados.
        HTTP Status: 201 (Criado), 400 (Faltam dados) ou 500 (Erro no banco).
        """
        # Verifica a presença dos campos obrigatórios mapeados no banco[cite: 9]
        if not id_sessao or not status:
            return {"erro": "Os campos 'id_sessao' e 'status' são obrigatórios."}, 400

        try:
            # Envia os dados convertidos de acordo com a assinatura do model[cite: 9]
            novo_pedido = Pedido_model.inserir_pedido(
                id_sessao=int(id_sessao),
                status=str(status),
                valor_total=float(valor_total or 0.0),
                tempo_estimado=int(tempo_estimado) if tempo_estimado is not None else None,
                endereco_entrega=str(endereco_entrega) if endereco_entrega else None
            )
            return {
                "mensagem": "Pedido criado com sucesso.",
                "pedido": PedidoController._serializar_pedido(novo_pedido)
            }, 201
        except SQLAlchemyError:
            # Pode ocorrer caso id_sessao não exista na tabela 'sessao'
            return {"erro": "Erro ao tentar criar o pedido. Verifique se o id_sessao é válido."}, 500

    @staticmethod
    def obter_por_id(id_pedido):
        """Busca um pedido específico pela chave primária[cite: 9]."""
        pedido = Pedido_model.obter_pedido(id_pedido)
        if not pedido:
            return {"erro": "Pedido não encontrado."}, 404

        return {"pedido": PedidoController._serializar_pedido(pedido)}, 200

    @staticmethod
    def obter_todos(filtros=None):
        """
        Lista pedidos. Pode ser filtrado por status ou id_sessao.
        """
        filtros = filtros or {}
        try:
            pedidos = Pedido_model.obter_todos(**filtros)
            # Retorna a lista serializada usando list comprehension
            return {"pedidos": [PedidoController._serializar_pedido(p) for p in pedidos]}, 200
        except ValueError as e:
            # Captura a rejeição caso tentem filtrar por colunas inexistentes[cite: 9]
            return {"erro": str(e)}, 400

    @staticmethod
    def atualizar(id_pedido, **kwargs):
        """
        Atualiza campos específicos de um pedido.
        Campos permitidos pelo model: 'status', 'valor_total', 'tempo_estimado', 'endereco_entrega'[cite: 9].
        """
        try:
            # O crud_model barra chaves inválidas (ValueError) e checa se o id_pedido existe[cite: 9]
            pedido_atualizado = Pedido_model.atualizar_pedido(id_pedido, **kwargs)
            
            if not pedido_atualizado:
                return {"erro": "Pedido não encontrado."}, 404
                
            return {
                "mensagem": "Pedido atualizado com sucesso.", 
                "pedido": PedidoController._serializar_pedido(pedido_atualizado)
            }, 200
            
        except ValueError as e:
            return {"erro": str(e)}, 400
        except SQLAlchemyError:
            return {"erro": "Erro interno ao atualizar os dados do pedido."}, 500

    @staticmethod
    def deletar(id_pedido):
        """Exclui o pedido. Vinculos de ItensPedido serão apagados via CASCADE[cite: 9]."""
        try:
            sucesso = Pedido_model.deletar_pedido(id_pedido)
            if not sucesso:
                return {"erro": "Pedido não encontrado."}, 404
                
            return {"mensagem": "Pedido deletado com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Erro ao tentar deletar o pedido. Restrições do banco podem impedir a ação."}, 409