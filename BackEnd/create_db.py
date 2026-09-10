
from app import create_app, db
from app.model.cliente import modeloCliente

app = create_app()
with app.app_context():
    db.create_all()
    print('Banco criado.')