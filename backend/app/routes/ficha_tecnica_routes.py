# Importações padrões do Flask para criação de sub-rotas e manuseio de JSON
from flask import Blueprint, jsonify, request

# Importa o controlador que processa as lógicas
from app.controllers.ficha_tecnica_controller import FichaTecnicaController

# Criação do Blueprint com a rota raiz bem definida
ficha_bp = Blueprint("ficha_tecnica", __name__, url_prefix="/api/fichas-tecnicas")

@ficha_bp.post("")
def criar_ficha():
    """Rota para vincular um ingrediente a um prato."""
    dados = request.get_json(silent=True) or {}
    resposta, status = FichaTecnicaController.criar(
        id_prato=dados.get("id_prato"),
        id_ingrediente=dados.get("id_ingrediente"),
        quantidade_necessaria=dados.get("quantidade_necessaria")
    )
    return jsonify(resposta), status

@ficha_bp.get("")
def listar_fichas():
    # Pega os dados originais (tudo em string)
    filtros_recebidos = request.args.to_dict()
    
    # Cria um novo dicionário para armazenar os dados com os tipos corretos
    filtros = {}
    
    for chave, valor in filtros_recebidos.items():
        # Se for um número (como id_prato ou id_ingrediente), converte para int
        if valor.isdigit():
            filtros[chave] = int(valor)
        else:
            filtros[chave] = valor

    resposta, status = FichaTecnicaController.obter_todos(filtros)
    return jsonify(resposta), status

@ficha_bp.get("/<int:id_prato>/ingredientes/<int:id_ingrediente>")
def obter_ficha(id_prato, id_ingrediente):
    """Rota para consultar uma associação exata utilizando a chave composta."""
    resposta, status = FichaTecnicaController.obter_por_id(id_prato, id_ingrediente)
    return jsonify(resposta), status

@ficha_bp.patch("/<int:id_prato>/ingredientes/<int:id_ingrediente>")
def atualizar_ficha(id_prato, id_ingrediente):
    """Rota para atualizar apenas a quantidade necessária daquela associação."""
    dados = request.get_json(silent=True) or {}
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização."}), 400
        
    resposta, status = FichaTecnicaController.atualizar(id_prato, id_ingrediente, **dados)
    return jsonify(resposta), status

@ficha_bp.delete("/<int:id_prato>/ingredientes/<int:id_ingrediente>")
def deletar_ficha(id_prato, id_ingrediente):
    """Rota para remover a associação entre o prato e o ingrediente."""
    resposta, status = FichaTecnicaController.deletar(id_prato, id_ingrediente)
    return jsonify(resposta), status