from flask import Flask, jsonify

from config import Config

from app.extensions import db

def criar_app(configuracao=None):
    """Cria e configura a aplicação Flask do Sabor e Clic."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if configuracao:
        app.config.update(configuracao)

    db.init_app(app)

    @app.get("/api")
    def status_api():
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
        return jsonify({"erro": "Recurso não encontrado."}), 404

    @app.errorhandler(405)
    def metodo_nao_permitido(_erro):
        return jsonify({"erro": "Método não permitido para esta rota."}), 405

    return app
