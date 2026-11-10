"""The active API is registered in api_routes; legacy route modules are not mounted."""
from app.routes.api_routes import api_bp

__all__ = ['api_bp']
