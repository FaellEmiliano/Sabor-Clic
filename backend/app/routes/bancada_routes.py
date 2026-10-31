from flask import Blueprint, jsonify, request
from app.controllers.bancada_controller import BancadaController

# Prefixo da API configurado sem a barra final para evitar conflitos no Flask
bancada_bp = Blueprint("bancada", __name__, url_prefix="/api/bancadas")

@bancada_bp.post("")
def criar_bancada():
    dados = request.get_json(silent=True) or {}
    resposta, status = BancadaController.criar(
        nome=dados.get("nome"),
        valor_hora=dados.get("valor_hora"),
        descricao=dados.get("descricao"),
        ativa=dados.get("ativa", True)
    )
    return jsonify(resposta), status

@bancada_bp.get("")
def listar_bancadas():
    resposta, status = BancadaController.obter_todos()
    return jsonify(resposta), status

@bancada_bp.get("/<int:id_bancada>")
def obter_bancada(id_bancada):
    resposta, status = BancadaController.obter_por_id(id_bancada)
    return jsonify(resposta), status

@bancada_bp.patch("/<int:id_bancada>")
def atualizar_bancada(id_bancada):
    dados = request.get_json(silent=True) or {}
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização."}), 400
        
    resposta, status = BancadaController.atualizar(id_bancada, **dados)
    return jsonify(resposta), status

@bancada_bp.patch("/<int:id_bancada>/status")
def alternar_status(id_bancada):
    resposta, status = BancadaController.alternar_status(id_bancada)
    return jsonify(resposta), status

@bancada_bp.delete("/<int:id_bancada>")
def deletar_bancada(id_bancada):
    resposta, status = BancadaController.deletar(id_bancada)
    return jsonify(resposta), status