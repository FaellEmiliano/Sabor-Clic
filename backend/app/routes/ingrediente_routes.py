# Importa módulos do Flask essenciais para criar rotas e lidar com JSON
from flask import Blueprint, jsonify, request

# Importa o controlador de ingredientes recém-criado
from app.controllers.ingrediente_controller import IngredienteController

# Criação do Blueprint com a raiz /api/ingredientes já definida
ingrediente_bp = Blueprint("ingrediente", __name__, url_prefix="/api/ingredientes")

@ingrediente_bp.post("")
def criar_ingrediente():
    """Rota para cadastrar um novo ingrediente (POST)."""
    # Extrai os dados do corpo da requisição com proteção contra falhas (silent=True)
    dados = request.get_json(silent=True) or {}
    
    resposta, status = IngredienteController.criar(
        nome=dados.get("nome"),
        unidade_medida=dados.get("unidade_medida"),
        quantidade_estoque=dados.get("quantidade_estoque", 0.0) # Usa 0.0 como padrão de segurança se vier nulo
    )
    return jsonify(resposta), status

@ingrediente_bp.get("")
def listar_ingredientes():
    """Rota para listar todos os ingredientes cadastrados (GET)."""
    resposta, status = IngredienteController.obter_todos()
    return jsonify(resposta), status

@ingrediente_bp.get("/<int:id_ingrediente>")
def obter_ingrediente(id_ingrediente):
    """Rota para obter dados detalhados de um único ingrediente utilizando o ID da URL."""
    resposta, status = IngredienteController.obter_por_id(id_ingrediente)
    return jsonify(resposta), status

@ingrediente_bp.patch("/<int:id_ingrediente>")
def atualizar_ingrediente(id_ingrediente):
    """Rota para atualização parcial dos dados do ingrediente (PATCH)."""
    dados = request.get_json(silent=True) or {}
    
    # Valida rapidamente para não processar requisições em branco
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização."}), 400
        
    # Desempacota o payload inteiro para os kwargs do controller
    resposta, status = IngredienteController.atualizar(id_ingrediente, **dados)
    return jsonify(resposta), status

@ingrediente_bp.delete("/<int:id_ingrediente>")
def deletar_ingrediente(id_ingrediente):
    """Rota para remover o ingrediente do banco de dados permanentemente (DELETE)."""
    resposta, status = IngredienteController.deletar(id_ingrediente)
    return jsonify(resposta), status