from flask import Blueprint, jsonify, request

from app.controllers.sessao_controller import criar_sessao, encerrar_sessao, obter_sessao

sessao_bp = Blueprint("sessao", __name__, url_prefix="/api")


@sessao_bp.post("/sessoes")
def sessoes():
    resposta, status = criar_sessao(request.get_json(silent=True) or {})
    return jsonify(resposta), status


@sessao_bp.get("/sessoes/<int:id_sessao>")
def sessao_por_id(id_sessao):
    resposta, status = obter_sessao(id_sessao)
    return jsonify(resposta), status


@sessao_bp.post("/sessoes/<int:id_sessao>/encerrar")
def encerrar(id_sessao):
    resposta, status = encerrar_sessao(id_sessao)
    return jsonify(resposta), status
