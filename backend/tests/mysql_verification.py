"""Run explicitly from backend/: python -m tests.mysql_verification.
Creates and removes only randomly named sabor_clic_qa_* schemas; never changes DB_NAME data.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta,timezone
from decimal import Decimal
from threading import Barrier
from uuid import uuid4
from tempfile import TemporaryDirectory
from pathlib import Path
from sqlalchemy import create_engine,text
from werkzeug.security import generate_password_hash
from config import Config
from app import criar_app,models as m
from app.extensions import db
from app.database import initialize,seed,run_script
from app.controllers.http import now


def run():
    import os
    source=os.environ.get('QA_DATABASE_URL') or Config.environment()['SQLALCHEMY_DATABASE_URI']
    if isinstance(source,str):
        from sqlalchemy.engine import make_url
        source=make_url(source)
    schema='sabor_clic_qa_'+uuid4().hex[:12]
    assert schema!=source.database and schema.startswith('sabor_clic_qa_')
    server=create_engine(source)
    with server.begin() as connection:connection.exec_driver_sql('CREATE DATABASE `'+schema+'` CHARACTER SET utf8mb4')
    app=criar_app({'TESTING':True,'SECRET_KEY':'mysql-qa-only','SQLALCHEMY_DATABASE_URI':source.set(database=schema),'LOGIN_IP_LIMIT':100})
    try:
        with app.app_context():
            initialize();initialize()
            seed(generate_password_hash('Teste1234'));seed(generate_password_hash('Ignored1234'))
            assert db.session.scalar(db.select(db.func.count()).select_from(m.Usuario))==3
            assert db.session.scalar(text('SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema=DATABASE()'))==0
            ingredient=db.session.scalar(db.select(m.Ingrediente).where(m.Ingrediente.nome=='Arroz demonstração'))
            iid=ingredient.id_ingrediente
            assert ingredient.quantidade_estoque==10
            client_user=m.Usuario_model.obter_usuario_email('cliente@demo.local')
            bench=m.Bancada_model.obter_todos()[0]
            dish=m.Prato_model.obter_todos()[0]
            bid,pid,uid=bench.id_bancada,dish.id_prato,client_user.id_usuario
            reservation=m.Reserva_model.inserir_reserva(uid,bid,now()-timedelta(minutes=1),now()+timedelta(hours=1),'em_andamento',20)
            sid=m.Sessao_model.inserir_sessao(reservation.id_reserva,'QA-1','ativa',iniciado_em=now()).id_sessao
            other_bench=m.Bancada_model.inserir_bancada('Concorrência',20)
            reservation=m.Reserva_model.inserir_reserva(uid,other_bench.id_bancada,now()-timedelta(minutes=1),now()+timedelta(hours=1),'em_andamento',20)
            sid2=m.Sessao_model.inserir_sessao(reservation.id_reserva,'QA-2','ativa',iniciado_em=now()).id_sessao
        def login(email='cliente@demo.local'):
            client=app.test_client();r=client.post('/api/login',json={'email':email,'senha':'Teste1234'})
            assert r.status_code==200,r.json
            return client,{'X-CSRF-Token':r.json['csrf_token']}
        client,headers=login();key=uuid4().hex
        body={'id_sessao':sid,'itens':[{'id_prato':pid,'quantidade':2}]}
        headers['Idempotency-Key']=key
        first=client.post('/api/pedidos',json=body,headers=headers);assert first.status_code==201,first.json
        second=client.post('/api/pedidos',json=body,headers=headers);assert second.json['pedido']['id_pedido']==first.json['pedido']['id_pedido']
        with app.app_context():assert db.session.get(m.Ingrediente,iid).quantidade_estoque==Decimal('9.600')
        admin,admin_headers=login('admin@demo.local')
        r=admin.patch('/api/pedidos/'+str(first.json['pedido']['id_pedido']),json={'status':'cancelado'},headers=admin_headers)
        assert r.status_code==200,r.json
        with app.app_context():assert db.session.get(m.Ingrediente,iid).quantidade_estoque==10
        old=client.get_cookie('session').value
        assert client.post('/api/logout',json={},headers=headers).status_code==200
        replay=app.test_client();replay.set_cookie('session',old);assert replay.get('/api/me').status_code==401
        # A whole-order lock on shared ingredients prevents overselling across distinct sessions.
        with app.app_context():
            from app.controllers.estoque_controller import movement
            movement(iid,Decimal('-9'),'ajuste')
            for ingredient in db.session.scalars(db.select(m.Ingrediente).where(m.Ingrediente.id_ingrediente!=iid)):
                movement(ingredient.id_ingrediente,-ingredient.quantidade_estoque,'ajuste')
            db.session.commit()
        barrier=Barrier(2)
        def checkout(sid):
            client,headers=login();headers['Idempotency-Key']=uuid4().hex;barrier.wait(timeout=10)
            return client.post('/api/pedidos',json={'id_sessao':sid,'itens':[{'id_prato':pid,'quantidade':4}]},headers=headers).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:results=sorted(pool.map(checkout,[sid,sid2]))
        assert results==[201,409],results
        with app.app_context():assert db.session.get(m.Ingrediente,iid).quantidade_estoque==Decimal('.200')
        # Two simultaneous reservations on a fresh interval: one winner only.
        barrier=Barrier(2)
        start=(now()+timedelta(days=2)).replace(tzinfo=timezone.utc)
        def reserve(_):
            client,headers=login();barrier.wait(timeout=10)
            return client.post('/api/reservas',json={'id_bancada':bid,'inicio':start.isoformat(),'fim':(start+timedelta(hours=1)).isoformat()},headers=headers).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:results=sorted(pool.map(reserve,[1,2]))
        assert results==[201,409],results
        with app.app_context():
            with db.engine.begin() as connection:run_script(connection,'11_queries_relatorios.sql')
        # Backup/restore round-trip, in the same disposable schema after clearing test-only rows.
        from app.database import backup,restore
        with app.app_context(),TemporaryDirectory(prefix='sabor-backup-qa-') as directory:
            path=Path(directory)/'snapshot.json'
            backup(path)
            expected={name:db.session.scalar(text('SELECT COUNT(*) FROM `'+name+'`')) for name in db.metadata.tables}
            balances={i.id_ingrediente:i.quantidade_estoque for i in m.Ingrediente_model.obter_todos()}
            db.session.remove()
            with db.engine.begin() as connection:
                connection.exec_driver_sql('SET FOREIGN_KEY_CHECKS=0')
                try:
                    for name in db.metadata.tables:connection.exec_driver_sql('DELETE FROM `'+name+'`')
                finally:connection.exec_driver_sql('SET FOREIGN_KEY_CHECKS=1')
            restore(path)
            for name,count in expected.items():assert db.session.scalar(text('SELECT COUNT(*) FROM `'+name+'`'))==count
            for iid,balance in balances.items():assert db.session.get(m.Ingrediente,iid).quantidade_estoque==balance
        print('MYSQL QA OK: esquema atual, seeds, sem triggers, baixa, estorno, logout, idempotência, backup/restauração, relatórios SQL e concorrência de estoque/reservas.')
    finally:
        with app.app_context():db.session.remove();db.engine.dispose()
        assert schema.startswith('sabor_clic_qa_') and len(schema)==26 and schema!=source.database
        with server.begin() as connection:connection.exec_driver_sql('DROP DATABASE `'+schema+'`')
        server.dispose()

if __name__=='__main__':run()
