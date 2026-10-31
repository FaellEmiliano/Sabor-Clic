# Importações vitais do Flask para gerenciamento da API
from flask import Blueprint, jsonify, request

# Importa o controlador de reservas
from app.controllers.reserva_controller import ReservaController

# Inicializa o Blueprint da reserva com o endpoint padrão
reserva_bp = Blueprint("reserva", __name__, url_prefix="/api/reservas")

@reserva_bp.post("")
def criar_reserva():
    """Rota para efetuar o agendamento de uma nova bancada (POST)."""
    dados = request.get_json(silent=True) or {}
    
    resposta, status = ReservaController.criar(
        id_cliente=dados.get("id_cliente"),
        id_bancada=dados.get("id_bancada"),
        inicio=dados.get("inicio"),
        fim=dados.get("fim"),
        status=dados.get("status"),
        valor_total=dados.get("valor_total", 0.0) # Usa float explicitamente por causa da assinatura[cite: 11]
    )
    return jsonify(resposta), status

@reserva_bp.get("")
def listar_reservas():
    """
    Rota para listar as reservas (GET).
    Aplica o casting seguro do request.args para agradar ao Pylance.
    """
    filtros_recebidos = request.args.to_dict()
    filtros = {}
    
    for chave, valor in filtros_recebidos.items():
        if valor.isdigit():
            # Converte chaves FK como id_cliente, id_bancada ou id_reserva
            filtros[chave] = int(valor)
        else:
            try:
                # Caso ocorra filtro pelo valor total numérico
                filtros[chave] = float(valor)
            except ValueError:
                # Mantém strings de status (ex: "confirmada") e strings ISO de data (ex: "2024-12-01")
                filtros[chave] = valor

    resposta, status = ReservaController.obter_todos(filtros)
    return jsonify(resposta), status

@reserva_bp.get("/<int:id_reserva>")
def obter_reserva(id_reserva):
    """Rota para consultar as informações de um agendamento específico."""
    resposta, status = ReservaController.obter_por_id(id_reserva)
    return jsonify(resposta), status

@reserva_bp.patch("/<int:id_reserva>")
def atualizar_reserva(id_reserva):
    """Rota para atualização de dados (como mudar o status de pendente para finalizado)."""
    dados = request.get_json(silent=True) or {}
    
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização."}), 400
        
    resposta, status = ReservaController.atualizar(id_reserva, **dados)
    return jsonify(resposta), status

@reserva_bp.delete("/<int:id_reserva>")
def deletar_reserva(id_reserva):
    """Rota para cancelamento/deleção direta da reserva."""
    resposta, status = ReservaController.deletar(id_reserva)
    return jsonify(resposta), status