# Importações cruciais do Flask para roteamento HTTP e gestão de JSON
from flask import Blueprint, jsonify, request

# Importa o controller configurado para substituições
from app.controllers.substituicao_controller import SubstituicaoController

# Definição do blueprint (agrupador de rotas)
substituicao_bp = Blueprint("substituicao", __name__, url_prefix="/api/substituicoes")

@substituicao_bp.post("")
def criar_substituicao():
    """Rota POST para criar a correlação entre dois ingredientes."""
    dados = request.get_json(silent=True) or {}
    
    resposta, status = SubstituicaoController.criar(
        id_ingrediente_original=dados.get("id_ingrediente_original"),
        id_ingrediente_substituto=dados.get("id_ingrediente_substituto"),
        prioridade=dados.get("prioridade", 1), # Padroniza int de acordo com a modelagem[cite: 13]
        fator_conversao=dados.get("fator_conversao", 1.0) # Padroniza float explicitamente[cite: 13]
    )
    return jsonify(resposta), status

@substituicao_bp.get("")
def listar_substituicoes():
    """
    Rota GET que lista todas as substituições. 
    Lida com o casting adequado para evitar avisos no Pylance.
    """
    filtros_recebidos = request.args.to_dict()
    filtros = {}
    
    # Processa os Query Parameters dinamicamente da URL
    for chave, valor in filtros_recebidos.items():
        if valor.isdigit():
            # Converte IDs e prioridades
            filtros[chave] = int(valor)
        else:
            try:
                # Converte fator de conversão quebrado (ex: ?fator_conversao=1.5)
                filtros[chave] = float(valor)
            except ValueError:
                filtros[chave] = valor

    resposta, status = SubstituicaoController.obter_todos(filtros)
    return jsonify(resposta), status

@substituicao_bp.get("/<int:id_original>/substitutos/<int:id_substituto>")
def obter_substituicao(id_original, id_substituto):
    """Rota GET formatada especialmente para buscar a tupla da chave composta."""
    resposta, status = SubstituicaoController.obter_por_id(id_original, id_substituto)
    return jsonify(resposta), status

@substituicao_bp.patch("/<int:id_original>/substitutos/<int:id_substituto>")
def atualizar_substituicao(id_original, id_substituto):
    """Rota PATCH voltada a editar prioridades e fatores de conversão."""
    dados = request.get_json(silent=True) or {}
    
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização."}), 400
        
    resposta, status = SubstituicaoController.atualizar(id_original, id_substituto, **dados)
    return jsonify(resposta), status

@substituicao_bp.delete("/<int:id_original>/substitutos/<int:id_substituto>")
def deletar_substituicao(id_original, id_substituto):
    """Rota DELETE voltada a desfazer a ligação de substituição entre os ingredientes."""
    resposta, status = SubstituicaoController.deletar(id_original, id_substituto)
    return jsonify(resposta), status