from app.routes.auth_routes import auth_bp
from app.routes.pedido_routes import pedido_bp
from app.routes.reserva_routes import reserva_bp
from app.routes.sessao_routes import sessao_bp

blueprints = (auth_bp, reserva_bp, sessao_bp, pedido_bp)
