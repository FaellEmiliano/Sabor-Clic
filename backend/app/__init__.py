from flask import Flask, request, session
from config import Config
from app.model.usuario_model import Usuario_model

def criar_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    from app.controller.auth_controller import auth_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    Usuario_model.criar_tabela()
    return app

app = criar_app()