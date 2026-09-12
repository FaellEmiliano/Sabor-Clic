from flask import Blueprint, jsonify, request

from app.controllers.auth_controller import cadastrar_cliente, obter_usuario, realizar_login

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.post("/cadastro")
def cadastro():
    resposta, status = cadastrar_cliente(request.get_json(silent=True) or {})
    return jsonify(resposta), status


@auth_bp.get("/cadastro/<int:id_usuario>")
def cadastro_por_id(id_usuario):
    resposta, status = obter_usuario(id_usuario)
    return jsonify(resposta), status


@auth_bp.post("/login")
def login():
    resposta, status = realizar_login(request.get_json(silent=True) or {})
    return jsonify(resposta), status
