# Importa recursos essenciais do Flask
from flask import Blueprint, jsonify, request

# Importa o controller correspondente
from app.controllers.prato_controller import PratoController

# Agrupa as rotas de gerenciamento de pratos, unificando o acesso em '/api/pratos'
prato_bp = Blueprint("prato", __name__, url_prefix="/api/pratos")

@prato_bp.post("")
def criar_prato():
    """Rota para adição de um novo prato no sistema (POST)."""
    dados = request.get_json(silent=True) or {}
    
    resposta, status = PratoController.criar(
        nome=dados.get("nome"),
        preco=dados.get("preco"),
        descricao=dados.get("descricao"),
        ativo=dados.get("ativo", True) # Fallback padrão é nascer ativo no cardápio
    )
    return jsonify(resposta), status

@prato_bp.get("")
def listar_pratos():
    """
    Rota para listar todos os pratos (GET).
    Lida com filtros dinâmicos na Query String (ex: ?ativo=true, ?preco=15.50).
    """
    filtros_recebidos = request.args.to_dict()
    filtros = {}
    
    # Tratamento de tipagem preventiva para Pylance e segurança do banco
    for chave, valor in filtros_recebidos.items():
        if valor.isdigit():
            # Converte números inteiros
            filtros[chave] = int(valor)
        elif valor.lower() in ["true", "false"]:
            # Trata booleanos vindos da URL (muito comum para filtrar pratos ativos)
            filtros[chave] = True if valor.lower() == "true" else False
        else:
            try:
                # Trata números decimais (ex: preco=25.50)
                filtros[chave] = float(valor)
            except ValueError:
                filtros[chave] = valor

    resposta, status = PratoController.obter_todos(filtros)
    return jsonify(resposta), status

@prato_bp.get("/<int:id_prato>")
def obter_prato(id_prato):
    """Rota para recuperar um prato exato utilizando seu ID."""
    resposta, status = PratoController.obter_por_id(id_prato)
    return jsonify(resposta), status

@prato_bp.patch("/<int:id_prato>")
def atualizar_prato(id_prato):
    """Rota para edição pontual dos dados do prato via PATCH."""
    dados = request.get_json(silent=True) or {}
    
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização."}), 400
        
    resposta, status = PratoController.atualizar(id_prato, **dados)
    return jsonify(resposta), status

@prato_bp.patch("/<int:id_prato>/status")
def alternar_status(id_prato):
    """Rota exclusiva e isolada para ligar ou desligar o prato no cardápio."""
    resposta, status = PratoController.alternar_status(id_prato)
    return jsonify(resposta), status

@prato_bp.delete("/<int:id_prato>")
def deletar_prato(id_prato):
    """Rota para exclusão completa do prato do banco de dados (DELETE)."""
    resposta, status = PratoController.deletar(id_prato)
    return jsonify(resposta), status