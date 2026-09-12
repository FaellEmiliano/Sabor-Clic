from flask import Blueprint, jsonify, request

from app.controllers.reserva_controller import criar_reserva, listar_bancadas, obter_reserva

reserva_bp = Blueprint("reserva", __name__, url_prefix="/api")


@reserva_bp.get("/bancadas")
def bancadas():
    resposta, status = listar_bancadas()
    return jsonify(resposta), status


@reserva_bp.post("/reservas")
def reservas():
    resposta, status = criar_reserva(request.get_json(silent=True) or {})
    return jsonify(resposta), status


@reserva_bp.get("/reservas/<int:id_reserva>")
def reserva_por_id(id_reserva):
    resposta, status = obter_reserva(id_reserva)
    return jsonify(resposta), status
