from flask import Blueprint, jsonify, request

from app.controllers.pedido_controller import criar_pedido, listar_cardapio, listar_kds, obter_pedido

pedido_bp = Blueprint("pedido", __name__, url_prefix="/api")


@pedido_bp.get("/cardapio")
def cardapio():
    resposta, status = listar_cardapio()
    return jsonify(resposta), status


@pedido_bp.post("/pedido/cadastro")
def cadastro_pedido():
    resposta, status = criar_pedido(request.get_json(silent=True) or {})
    return jsonify(resposta), status


@pedido_bp.get("/pedido/<int:id_pedido>")
def pedido_por_id(id_pedido):
    resposta, status = obter_pedido(id_pedido)
    return jsonify(resposta), status


@pedido_bp.get("/kds")
def kds():
    resposta, status = listar_kds()
    return jsonify(resposta), status


@pedido_bp.get("/kds/<int:id_pedido>")
def kds_por_id(id_pedido):
    resposta, status = listar_kds(id_pedido)
    return jsonify(resposta), status
