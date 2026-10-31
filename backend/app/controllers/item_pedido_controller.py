# Importa o tratamento de erros do SQLAlchemy para evitar travamento da API
from sqlalchemy.exc import SQLAlchemyError

# Importa o model que gerencia o acesso à tabela item_pedido no banco de dados[cite: 8]
from app.models.item_pedido_model import ItemPedido_model

class ItemPedidoController:
    """Controlador responsável por processar as regras de negócio dos itens de um pedido."""

    @staticmethod
    def _serializar_item(item):
        """
        Método auxiliar (DRY) para converter a entidade SQLAlchemy em dicionário.
        Trata a conversão dos tipos Numeric (preco_unitario e subtotal) para float[cite: 8],
        e mantém os IDs e quantidade como inteiros.
        """
        return {
            "id_item_pedido": item.id_item_pedido,
            "id_pedido": item.id_pedido,
            "id_prato": item.id_prato,
            "quantidade": item.quantidade,
            "preco_unitario": float(item.preco_unitario) if item.preco_unitario is not None else 0.0,
            "subtotal": float(item.subtotal) if item.subtotal is not None else 0.0
        }

    @staticmethod
    def criar(id_pedido, id_prato, quantidade, preco_unitario, subtotal):
        """
        Valida os dados e insere um novo item_pedido.
        Todos os campos são obrigatórios segundo a definição do banco[cite: 8].
        """
        # Verifica se algum campo obrigatório está faltando (None ou vazio)
        if not id_pedido or not id_prato or quantidade is None or preco_unitario is None or subtotal is None:
            return {"erro": "Todos os campos (id_pedido, id_prato, quantidade, preco_unitario, subtotal) são obrigatórios."}, 400

        # Validação preventiva baseada na CheckConstraint ('quantidade > 0') do model[cite: 8]
        if int(quantidade) <= 0:
            return {"erro": "A quantidade do item deve ser maior que zero."}, 400

        try:
            # Envia os dados rigorosamente de acordo com a assinatura do model[cite: 8]
            novo_item = ItemPedido_model.inserir_item_pedido(
                id_pedido=int(id_pedido),
                id_prato=int(id_prato),
                quantidade=int(quantidade),
                preco_unitario=float(preco_unitario),
                subtotal=float(subtotal)
            )
            return {
                "mensagem": "Item adicionado ao pedido com sucesso.",
                "item_pedido": ItemPedidoController._serializar_item(novo_item)
            }, 201
        except SQLAlchemyError:
            return {"erro": "Erro interno ao tentar adicionar o item ao pedido. Verifique os IDs informados."}, 500

    @staticmethod
    def obter_por_id(id_item_pedido):
        """Busca um item de pedido específico pela sua chave primária[cite: 8]."""
        item = ItemPedido_model.obter_item_pedido(id_item_pedido)
        if not item:
            return {"erro": "Item do pedido não encontrado."}, 404

        return {"item_pedido": ItemPedidoController._serializar_item(item)}, 200

    @staticmethod
    def obter_todos(filtros=None):
        """
        Retorna uma lista de itens filtrada ou completa. 
        Útil para buscar todos os itens de um id_pedido específico[cite: 8].
        """
        filtros = filtros or {}
        try:
            itens = ItemPedido_model.obter_todos(**filtros)
            return {"itens_pedido": [ItemPedidoController._serializar_item(i) for i in itens]}, 200
        except ValueError as e:
            return {"erro": str(e)}, 400

    @staticmethod
    def atualizar(id_item_pedido, **kwargs):
        """
        Atualiza campos específicos de um item existente (ex: quantidade, preco_unitario)[cite: 8].
        Bloqueia quantidades negativas antes de chegar no banco.
        """
        # Checa a constraint de quantidade caso ela esteja sendo alterada
        if 'quantidade' in kwargs and int(kwargs['quantidade']) <= 0:
            return {"erro": "A quantidade deve ser maior que zero."}, 400

        try:
            # O crud_model levanta ValueError se tentar atualizar 'id_pedido', que não está nos campos permitidos[cite: 8]
            item_atualizado = ItemPedido_model.atualizar_item_pedido(id_item_pedido, **kwargs)
            
            if not item_atualizado:
                return {"erro": "Item do pedido não encontrado."}, 404
                
            return {
                "mensagem": "Item atualizado com sucesso.", 
                "item_pedido": ItemPedidoController._serializar_item(item_atualizado)
            }, 200
            
        except ValueError as e:
            return {"erro": str(e)}, 400
        except SQLAlchemyError:
            return {"erro": "Erro interno ao atualizar o item do pedido."}, 500

    @staticmethod
    def deletar(id_item_pedido):
        """Remove permanentemente o item do pedido[cite: 8]."""
        try:
            sucesso = ItemPedido_model.deletar_item_pedido(id_item_pedido)
            if not sucesso:
                return {"erro": "Item do pedido não encontrado."}, 404
                
            return {"mensagem": "Item removido do pedido com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Erro ao tentar deletar o item. Podem existir vínculos restritos."}, 409