# Importa módulos padrão do Flask para registro de rotas e manipulação de requisições JSON
from flask import Blueprint, jsonify, request

# Importa o controller respectivo
from app.controllers.item_pedido_controller import ItemPedidoController

# Criação do Blueprint (grupo de rotas)
item_pedido_bp = Blueprint("item_pedido", __name__, url_prefix="/api/itens-pedido")

@item_pedido_bp.post("")
def criar_item_pedido():
    """Rota POST para adicionar um novo item a um pedido."""
    dados = request.get_json(silent=True) or {}
    
    # Extrai os dados sem definir default fallback (como 0 ou 0.0), delegando a validação de presença para o controller
    resposta, status = ItemPedidoController.criar(
        id_pedido=dados.get("id_pedido"),
        id_prato=dados.get("id_prato"),
        quantidade=dados.get("quantidade"),
        preco_unitario=dados.get("preco_unitario"),
        subtotal=dados.get("subtotal")
    )
    return jsonify(resposta), status

@item_pedido_bp.get("")
def listar_itens_pedido():
    """
    Rota GET para listar itens. 
    Aplica a técnica recomendada de construção de um novo dicionário para evitar erros do Pylance com tipagem.
    """
    filtros_recebidos = request.args.to_dict()
    filtros = {}
    
    # Faz o casting seguro dos valores passados via Query String (URL)
    for chave, valor in filtros_recebidos.items():
        if valor.isdigit():
            # Útil para filtrar por id_pedido=5 ou id_prato=2
            filtros[chave] = int(valor)
        else:
            try:
                # Tenta converter para float caso sejam filtros por preço (embora menos comum na URL)
                filtros[chave] = float(valor)
            except ValueError:
                filtros[chave] = valor

    resposta, status = ItemPedidoController.obter_todos(filtros)
    return jsonify(resposta), status

@item_pedido_bp.get("/<int:id_item_pedido>")
def obter_item_pedido(id_item_pedido):
    """Rota GET para recuperar dados de um item exato pelo seu ID."""
    resposta, status = ItemPedidoController.obter_por_id(id_item_pedido)
    return jsonify(resposta), status

@item_pedido_bp.patch("/<int:id_item_pedido>")
def atualizar_item_pedido(id_item_pedido):
    """Rota PATCH para alterar parcialmente os dados (ex: quantidade) de um item."""
    dados = request.get_json(silent=True) or {}
    
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização."}), 400
        
    resposta, status = ItemPedidoController.atualizar(id_item_pedido, **dados)
    return jsonify(resposta), status

@item_pedido_bp.delete("/<int:id_item_pedido>")
def deletar_item_pedido(id_item_pedido):
    """Rota DELETE para remover um item do carrinho/pedido."""
    resposta, status = ItemPedidoController.deletar(id_item_pedido)
    return jsonify(resposta), status