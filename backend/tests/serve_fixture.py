"""Disposable browser QA server: python -m tests.serve_fixture (from backend/)."""
from datetime import timedelta
import os
from decimal import Decimal
from tempfile import TemporaryDirectory
from pathlib import Path
from app import criar_app
from app.extensions import db
from app import models as m
from app.controllers.http import now

temporary = TemporaryDirectory(prefix='sabor-clic-qa-')
uri = 'sqlite:///' + str(Path(temporary.name) / 'qa.sqlite').replace('\\','/')
app = criar_app({'TESTING': True, 'SECRET_KEY': 'browser-test-only', 'SQLALCHEMY_DATABASE_URI': uri,
                 'UPLOAD_FOLDER': str(Path(temporary.name) / 'uploads')})
with app.app_context():
    db.create_all()
    client = m.Usuario_model.inserir_cliente('Cliente Teste', 'cliente@teste.com', 'Teste1234')
    m.Usuario_model.inserir_cozinheiro('Chef Teste', 'chef@teste.com', 'Teste1234')
    m.Usuario_model.inserir_administrador('Admin Teste', 'admin@teste.com', 'Teste1234')
    bench = m.Bancada_model.inserir_bancada('Toscana',Decimal('20'))
    m.Bancada_model.inserir_bancada('Provence',Decimal('30'))
    dish = m.Prato_model.inserir_prato('Risoto',Decimal('12.35'),descricao='Risoto fresco')
    ingredient = m.Ingrediente_model.inserir_ingrediente('Arroz','kg',Decimal('10'))
    m.Ingrediente_model.inserir_ingrediente('Quinoa','kg',Decimal('5'))
    m.FichaTecnica_model.inserir_ficha_tecnica(dish.id_prato,ingredient.id_ingrediente,Decimal('.2'))
    reservation = m.Reserva_model.inserir_reserva(client.id_usuario,bench.id_bancada,now()-timedelta(minutes=1),now()+timedelta(hours=2),'em_andamento',40)
    m.Sessao_model.inserir_sessao(reservation.id_reserva,'fixture-only','ativa',iniciado_em=now())

if __name__=='__main__':
    print('Fixture PID:',os.getpid(),flush=True)
    app.run(host='127.0.0.1',port=int(os.environ.get('QA_PORT','5051')),debug=False)
