# Importa recursos do Flask para definição de rotas e processamento de requests
from flask import Blueprint, jsonify, request

# Importa o controlador que processa as regras de negócio
from app.controllers.pedido_controller import PedidoController

# Inicializa o grupo de rotas da entidade 'pedido'
pedido_bp = Blueprint("pedido", __name__, url_prefix="/api/pedidos")

@pedido_bp.post("")
def criar_pedido():
    """Rota POST para abrir um novo pedido associado a uma sessão."""
    dados = request.get_json(silent=True) or {}
    
    resposta, status = PedidoController.criar(
        id_sessao=dados.get("id_sessao"),
        status=dados.get("status"),
        valor_total=dados.get("valor_total", 0), # Usa fallback 0 conforme assinatura[cite: 9]
        tempo_estimado=dados.get("tempo_estimado"),
        endereco_entrega=dados.get("endereco_entrega")
    )
    return jsonify(resposta), status

@pedido_bp.get("")
def listar_pedidos():
    """
    Rota GET para listar pedidos.
    Lida com a extração e o casting seguro da tipagem da Query String para o Pylance.
    """
    filtros_recebidos = request.args.to_dict()
    filtros = {}
    
    # Avalia chave a chave para aplicar a tipagem (int, float ou manter str)
    for chave, valor in filtros_recebidos.items():
        if valor.isdigit():
            # Converte chaves relacionais numéricas (ex: id_sessao=1) ou tempos
            filtros[chave] = int(valor)
        else:
            try:
                # Tenta formatar buscas que passem preço (ex: valor_total=50.50)
                filtros[chave] = float(valor)
            except ValueError:
                # Se não for número, assume que é String (ex: status='pendente')
                filtros[chave] = valor

    resposta, status = PedidoController.obter_todos(filtros)
    return jsonify(resposta), status

@pedido_bp.get("/<int:id_pedido>")
def obter_pedido(id_pedido):
    """Rota GET para buscar dados de um pedido específico via ID."""
    resposta, status = PedidoController.obter_por_id(id_pedido)
    return jsonify(resposta), status

@pedido_bp.patch("/<int:id_pedido>")
def atualizar_pedido(id_pedido):
    """Rota PATCH para alterar o status, tempo_estimado, etc[cite: 9]."""
    dados = request.get_json(silent=True) or {}
    
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização."}), 400
        
    resposta, status = PedidoController.atualizar(id_pedido, **dados)
    return jsonify(resposta), status

@pedido_bp.delete("/<int:id_pedido>")
def deletar_pedido(id_pedido):
    """Rota DELETE para remover completamente o pedido."""
    resposta, status = PedidoController.deletar(id_pedido)
    return jsonify(resposta), status
