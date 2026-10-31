# Importações cruciais do Flask para roteamento e manipulação de JSON
from flask import Blueprint, jsonify, request

# Importa o controlador que lida com a entidade Sessao
from app.controllers.sessao_controller import SessaoController

# Inicializa o Blueprint da sessão, agrupando as rotas no prefixo '/api/sessoes'
sessao_bp = Blueprint("sessao", __name__, url_prefix="/api/sessoes")

@sessao_bp.post("")
def criar_sessao():
    """Rota POST para gerar e associar uma nova sessão a uma reserva existente."""
    dados = request.get_json(silent=True) or {}
    
    resposta, status = SessaoController.criar(
        id_reserva=dados.get("id_reserva"),
        codigo_acesso=dados.get("codigo_acesso"),
        status=dados.get("status"),
        iniciado_em=dados.get("iniciado_em"),
        encerrado_em=dados.get("encerrado_em")
    )
    return jsonify(resposta), status

@sessao_bp.get("")
def listar_sessoes():
    """
    Rota GET para listagem de sessões.
    Utiliza casting seguro de parâmetros Query String para não acionar alertas no Pylance.
    """
    filtros_recebidos = request.args.to_dict()
    filtros = {}
    
    for chave, valor in filtros_recebidos.items():
        if valor.isdigit():
            # Converte as chaves relacionais, como id_sessao ou id_reserva, para int
            filtros[chave] = int(valor)
        else:
            # Mantém strings, especialmente 'status', 'codigo_acesso' e as datas ISO
            filtros[chave] = valor

    resposta, status = SessaoController.obter_todos(filtros)
    return jsonify(resposta), status

@sessao_bp.get("/<int:id_sessao>")
def obter_sessao(id_sessao):
    """Rota GET para buscar informações completas de uma única sessão via ID."""
    resposta, status = SessaoController.obter_por_id(id_sessao)
    return jsonify(resposta), status

@sessao_bp.patch("/<int:id_sessao>")
def atualizar_sessao(id_sessao):
    """
    Rota PATCH para atualização parcial (ex: registrar data em 'iniciado_em' ou mudar status).
    """
    dados = request.get_json(silent=True) or {}
    
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização."}), 400
        
    resposta, status = SessaoController.atualizar(id_sessao, **dados)
    return jsonify(resposta), status

@sessao_bp.delete("/<int:id_sessao>")
def deletar_sessao(id_sessao):
    """Rota DELETE para encerrar ou apagar uma sessão no banco de dados."""
    resposta, status = SessaoController.deletar(id_sessao)
    return jsonify(resposta), status