# Importações nativas do Flask[cite: 14]
from flask import Flask, jsonify

# Importação das configurações globais da aplicação[cite: 14]
from config import Config

# Importação do banco de dados instanciado[cite: 14]
from app.extensions import db

# ==========================================
# IMPORTAÇÃO DOS BLUEPRINTS (ROTAS)
# ==========================================
from app.routes.auth_routes import auth_bp
from app.routes.bancada_routes import bancada_bp
from app.routes.ficha_tecnica_routes import ficha_bp
from app.routes.ingrediente_routes import ingrediente_bp
from app.routes.item_pedido_routes import item_pedido_bp
from app.routes.pedido_routes import pedido_bp
from app.routes.prato_routes import prato_bp
from app.routes.reserva_routes import reserva_bp
from app.routes.sessao_routes import sessao_bp
from app.routes.substituicao_routes import substituicao_bp


def criar_app(configuracao=None):
    """Cria e configura a aplicação Flask do Sabor e Clic[cite: 14]."""
    
    # Inicializa a instância do Flask[cite: 14]
    app = Flask(__name__)
    
    # Carrega as configurações a partir do objeto Config[cite: 14]
    app.config.from_object(Config)

    # Permite sobrescrever configurações para testes, caso algo seja passado no parâmetro[cite: 14]
    if configuracao:
        app.config.update(configuracao)

    # Vincula o SQLAlchemy à instância do aplicativo Flask[cite: 14]
    db.init_app(app)

    # ==========================================
    # REGISTRO DOS BLUEPRINTS
    # ==========================================
    # Acopla cada grupo de rotas à aplicação principal
    app.register_blueprint(auth_bp)
    app.register_blueprint(bancada_bp)
    app.register_blueprint(ficha_bp)
    app.register_blueprint(ingrediente_bp)
    app.register_blueprint(item_pedido_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(prato_bp)
    app.register_blueprint(reserva_bp)
    app.register_blueprint(sessao_bp)
    app.register_blueprint(substituicao_bp)

    # ==========================================
    # ROTAS BASE E TRATAMENTO DE ERROS GLOBAIS
    # ==========================================
    
    @app.get("/api")
    def status_api():
        """Retorna o status geral da API para monitoramento de health check[cite: 14]."""
        return jsonify(
            {
                "aplicacao": "Sabor e Clic",
                "status": "online",
                "persistencia": "banco de dados",
                "fluxo": ["reserva", "sessao", "pedido", "kds"],
            }
        )

    @app.errorhandler(404)
    def recurso_nao_encontrado(_erro):
        """Captura tentativas de acesso a endpoints inexistentes[cite: 14]."""
        return jsonify({"erro": "Recurso não encontrado."}), 404

    @app.errorhandler(405)
    def metodo_nao_permitido(_erro):
        """Captura tentativas de usar verbos HTTP errados (ex: GET numa rota de POST)[cite: 14]."""
        return jsonify({"erro": "Método não permitido para esta rota."}), 405

    # Retorna o aplicativo pronto para rodar (ou para ser usado no gunicorn)[cite: 14]
    return app
