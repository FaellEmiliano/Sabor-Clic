from flask import Blueprint, jsonify, request
from app.controllers.auth_controller import UsuarioController

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

@auth_bp.post("/login")
def login():
    dados = request.get_json(silent=True) or {}
    resposta, status = UsuarioController.login(
        email=dados.get("email"),
        senha=dados.get("senha")
    )
    return jsonify(resposta), status

@auth_bp.post("/usuarios/cliente")
def cadastrar_cliente():
    dados = request.get_json(silent=True) or {}
    resposta, status = UsuarioController.cadastrar_cliente(
        nome=dados.get("nome"),
        email=dados.get("email"),
        senha=dados.get("senha"),
        endereco_entrega=dados.get("endereco_entrega"),
        ativo=dados.get("ativo", True)
    )
    return jsonify(resposta), status

@auth_bp.post("/usuarios/cozinheiro")
def cadastrar_cozinheiro():
    dados = request.get_json(silent=True) or {}
    resposta, status = UsuarioController.cadastrar_cozinheiro(
        nome=dados.get("nome"),
        email=dados.get("email"),
        senha=dados.get("senha"),
        turno=dados.get("turno"),
        especialidade=dados.get("especialidade"),
        ativo=dados.get("ativo", True)
    )
    return jsonify(resposta), status

@auth_bp.post("/usuarios/administrador")
def cadastrar_administrador():
    dados = request.get_json(silent=True) or {}
    resposta, status = UsuarioController.cadastrar_administrador(
        nome=dados.get("nome"),
        email=dados.get("email"),
        senha=dados.get("senha"),
        ativo=dados.get("ativo", True)
    )
    return jsonify(resposta), status

@auth_bp.get("/usuarios")
def obter_todos():
    resposta, status = UsuarioController.obter_todos()
    return jsonify(resposta), status

@auth_bp.get("/usuarios/<int:id_usuario>")
def obter_por_id(id_usuario):
    resposta, status = UsuarioController.obter_por_id(id_usuario)
    return jsonify(resposta), status

@auth_bp.patch("/usuarios/<int:id_usuario>")
def atualizar_usuario(id_usuario):
    dados = request.get_json(silent=True) or {}
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização."}), 400
        
    resposta, status = UsuarioController.atualizar(id_usuario, **dados)
    return jsonify(resposta), status

@auth_bp.patch("/usuarios/<int:id_usuario>/status")
def alternar_status(id_usuario):
    resposta, status = UsuarioController.alternar_status_ativo(id_usuario)
    return jsonify(resposta), status

@auth_bp.delete("/usuarios/<int:id_usuario>")
def deletar_usuario(id_usuario):
    resposta, status = UsuarioController.deletar(id_usuario)
    return jsonify(resposta), status