import unittest
from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal

from app import criar_app
from app.extensions import db
from app import models as m


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = criar_app({'TESTING': True, 'SECRET_KEY': 'test-only',
                              'SQLALCHEMY_DATABASE_URI': 'sqlite://'})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.session.execute(db.text('PRAGMA foreign_keys=ON'))
        db.session.commit()
        db.create_all()
        self.cliente = self.app.test_client()
        self.customer = m.Usuario_model.inserir_cliente('Cliente', 'cliente@teste.com', 'senha1234').id_usuario
        self.other = m.Usuario_model.inserir_cliente('Outro', 'outro@teste.com', 'senha1234').id_usuario
        m.Usuario_model.inserir_administrador('Admin', 'admin@teste.com', 'senha1234')
        m.Usuario_model.inserir_cozinheiro('Chef', 'chef@teste.com', 'senha1234')
        self.bench = m.Bancada_model.inserir_bancada('Toscana', Decimal('20')).id_bancada
        self.dish = m.Prato_model.inserir_prato('Prato', Decimal('12.35')).id_prato
        self.login('cliente@teste.com')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()

    def login(self, email):
        r = self.cliente.post('/api/login', json={'email': email, 'senha': 'senha1234'})
        self.assertEqual(r.status_code, 200, r.get_json())
        self.csrf = r.json['csrf_token']

    def send(self, method, path, data=None):
        return self.cliente.open(path, method=method, json=data,
                                 headers={'X-CSRF-Token': self.csrf, 'Idempotency-Key':str(uuid4())})

    def reserve(self):
        start = (datetime.now() + timedelta(days=1)).replace(microsecond=0)
        return self.send('POST', '/api/reservas', {
            'id_bancada': self.bench, 'inicio': start.isoformat(),
            'fim': (start + timedelta(hours=2)).isoformat(), 'valor_total': 0})

    def flow(self):
        r = self.reserve()
        self.assertEqual(r.status_code, 201, r.json)
        reservation = db.session.get(m.Reserva, r.json['reserva']['id_reserva'])
        from app.controllers.http import now
        reservation.inicio = now() - timedelta(minutes=1)
        reservation.fim = now() + timedelta(hours=2)
        db.session.commit()
        r = self.send('POST', '/api/sessoes', {'id_reserva': reservation.id_reserva})
        self.assertEqual(r.status_code, 201, r.json)
        return r.json['sessao']['id_sessao']

    def test_app_and_frontend_start(self):
        self.assertEqual(self.cliente.get('/api').status_code, 200)
        with self.cliente.get('/') as response:
            self.assertEqual(response.status_code, 200)
        self.assertEqual(self.cliente.get('/api/pratos').status_code, 200)

    def test_auth_and_csrf(self):
        self.assertEqual(self.cliente.post('/api/pedidos', json={}).status_code, 403)
        self.assertEqual(self.send('POST', '/api/usuarios/administrador', {}).status_code, 403)
        self.send('POST', '/api/logout', {})
        self.assertEqual(self.cliente.get('/api/reservas').status_code, 401)
        self.assertEqual(self.cliente.post('/api/login', json={'email': 'cliente@teste.com', 'senha': 'errada'}).status_code, 401)

    def test_reserva_calculates_total_and_rejects_overlap(self):
        r = self.reserve()
        self.assertEqual(r.status_code, 201, r.json)
        self.assertEqual(r.json['reserva']['valor_total'], 40)
        self.assertEqual(self.reserve().status_code, 409)

    def test_order_is_atomic_and_prices_are_server_side(self):
        sid = self.flow()
        r = self.send('POST', '/api/pedidos', {'id_sessao': sid, 'valor_total': 0,
            'itens': [{'id_prato': self.dish, 'quantidade': 2, 'preco_unitario': 0}]})
        self.assertEqual(r.status_code, 201, r.json)
        self.assertEqual(r.json['pedido']['valor_total'], 24.7)
        self.assertEqual(len(r.json['pedido']['itens']), 1)
        r = self.send('POST', '/api/pedidos', {'id_sessao': sid,
            'itens': [{'id_prato': self.dish, 'quantidade': 1}, {'id_prato': 999, 'quantidade': 1}]})
        self.assertEqual(r.status_code, 404, r.json)
        self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(m.Pedido)), 1)

    def test_customer_isolation(self):
        sid = self.flow()
        self.login('outro@teste.com')
        self.assertEqual(self.cliente.get('/api/reservas').json['reservas'], [])
        self.assertEqual(self.cliente.get(f'/api/sessoes/{sid}').status_code, 404)
        self.assertEqual(self.send('POST', '/api/pedidos', {'id_sessao': sid, 'itens': [{'id_prato': self.dish, 'quantidade': 1}]}).status_code, 404)

    def test_kds_and_session_close(self):
        sid = self.flow()
        r = self.send('POST', '/api/pedidos', {'id_sessao': sid, 'itens': [{'id_prato': self.dish, 'quantidade': 1}]})
        pid = r.json['pedido']['id_pedido']
        self.assertEqual(self.send('POST', f'/api/sessoes/{sid}/encerrar', {}).status_code, 409)
        self.login('chef@teste.com')
        self.assertEqual(self.cliente.get('/api/kds').json['pedidos'][0]['bancada'], 'Toscana')
        for status in ['em_preparo', 'pronto', 'entregue']:
            self.assertEqual(self.send('PATCH', f'/api/pedidos/{pid}', {'status': status}).status_code, 200)
        self.login('cliente@teste.com')
        self.assertEqual(self.send('POST', f'/api/sessoes/{sid}/encerrar', {}).status_code, 200)
        self.assertEqual(self.send('POST', '/api/pedidos', {'id_sessao': sid, 'itens': [{'id_prato': self.dish, 'quantidade': 1}]}).status_code, 409)

    def test_invalid_payloads_are_400(self):
        for payload in [[], 'texto', {'id_bancada': 'abc'}, {'id_bancada': self.bench, 'inicio': 'errada', 'fim': 'errada'}]:
            self.assertEqual(self.send('POST', '/api/reservas', payload).status_code, 400)
        self.login('admin@teste.com')
        for price in ['abc', -1, 'NaN', True]:
            self.assertEqual(self.send('POST', '/api/pratos', {'nome': 'Teste', 'preco': price}).status_code, 400)


    def test_password_change_invalidates_other_sessions(self):
        other = self.app.test_client()
        response = other.post('/api/login', json={'email':'cliente@teste.com','senha':'senha1234'})
        self.assertEqual(response.status_code,200)
        response = self.send('PATCH', f'/api/usuarios/{self.customer}', {'senha':'novasenha123'})
        self.assertEqual(response.status_code,200,response.json)
        self.assertEqual(self.cliente.get('/api/me').status_code,200)
        self.assertEqual(other.get('/api/me').status_code,401)

    def test_admin_user_update_is_atomic(self):
        self.login('admin@teste.com')
        response = self.send('PATCH', f'/api/usuarios/{self.customer}', {'nome':'Alterado','email':'outro@teste.com'})
        self.assertEqual(response.status_code,409)
        self.assertEqual(db.session.get(m.Usuario,self.customer).nome,'Cliente')

    def test_public_signup_has_no_privilege_escalation(self):
        self.send('POST','/api/logout',{})
        data={'nome':'Novo','email':'novo@teste.com','senha':'senha1234'}
        response=self.cliente.post('/api/usuarios/cliente',json=data)
        self.assertEqual(response.status_code,201,response.json)
        self.assertNotIn('senha_hash',response.json['usuario'])
        self.assertEqual(self.cliente.post('/api/usuarios/administrador',json=data).status_code,401)
        data.update(email='escalacao@teste.com',ativo=False)
        self.assertEqual(self.cliente.post('/api/usuarios/cliente',json=data).status_code,400)

    def test_origin_and_preflight(self):
        self.assertEqual(self.cliente.post('/api/login',json={},headers={'Origin':'https://estranho.example'}).status_code,403)
        self.app.config['CORS_ORIGINS']=['http://localhost:5500']
        response=self.cliente.options('/api/pedidos',headers={'Origin':'http://localhost:5500'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'],'http://localhost:5500')
        self.assertEqual(response.headers['Access-Control-Allow-Credentials'],'true')

    def test_catalog_composite_keys_and_restricted_delete(self):
        self.login('admin@teste.com')
        response=self.send('POST','/api/ingredientes',{'nome':'Arroz','unidade_medida':'kg','quantidade_estoque':10})
        self.assertEqual(response.status_code,201,response.json)
        iid=response.json['ingrediente']['id_ingrediente']
        response=self.send('POST','/api/fichas-tecnicas',{'id_prato':self.dish,'id_ingrediente':iid,'quantidade_necessaria':'.2'})
        self.assertEqual(response.status_code,201,response.json)
        path=f'/api/fichas-tecnicas/{self.dish}/ingredientes/{iid}'
        self.assertEqual(self.send('PATCH',path,{'quantidade_necessaria':'.3'}).status_code,200)
        self.assertEqual(self.send('DELETE',f'/api/ingredientes/{iid}').status_code,409)
        self.assertEqual(self.send('DELETE',path).status_code,200)
        # Stock adjustments are auditable history and prevent destructive deletion.
        self.assertEqual(self.send('DELETE',f'/api/ingredientes/{iid}').status_code,409)

    def test_substitutions_validate_factors_and_identity(self):
        self.login('admin@teste.com')
        a=m.Ingrediente_model.inserir_ingrediente('A','kg',1).id_ingrediente
        b=m.Ingrediente_model.inserir_ingrediente('B','kg',1).id_ingrediente
        for factor in [0,-1,'abc']:
            self.assertEqual(self.send('POST','/api/substituicoes',{'id_ingrediente_original':a,'id_ingrediente_substituto':b,'fator_conversao':factor}).status_code,400)
        self.assertEqual(self.send('POST','/api/substituicoes',{'id_ingrediente_original':a,'id_ingrediente_substituto':a}).status_code,400)
        self.assertEqual(self.send('POST','/api/substituicoes',{'id_ingrediente_original':a,'id_ingrediente_substituto':b}).status_code,201)
        self.assertEqual(self.send('PATCH',f'/api/substituicoes/{a}/substitutos/{b}',{'fator_conversao':2}).status_code,200)

    def test_kitchen_only_changes_availability_and_order_status(self):
        self.login('chef@teste.com')
        self.assertEqual(self.send('PATCH',f'/api/pratos/{self.dish}',{'ativo':False}).status_code,200)
        self.assertEqual(self.send('PATCH',f'/api/pratos/{self.dish}',{'preco':1}).status_code,403)
        self.assertEqual(self.cliente.get('/api/usuarios').status_code,403)
        self.assertEqual(self.cliente.get('/api/relatorios').status_code,403)

    def test_session_requires_reserved_period_and_no_duplicate(self):
        response=self.reserve()
        rid=response.json['reserva']['id_reserva']
        self.assertEqual(self.send('POST','/api/sessoes',{'id_reserva':rid}).status_code,409)
        reservation=db.session.get(m.Reserva,rid)
        from app.controllers.http import now
        reservation.inicio=now()-timedelta(minutes=1)
        reservation.fim=now()+timedelta(hours=1)
        db.session.commit()
        self.assertEqual(self.send('POST','/api/sessoes',{'id_reserva':rid}).status_code,201)
        self.assertEqual(self.send('POST','/api/sessoes',{'id_reserva':rid}).status_code,409)
        self.assertEqual(self.send('PATCH',f'/api/reservas/{rid}',{'status':'cancelada'}).status_code,409)

    def test_invalid_order_has_no_rows_and_no_direct_item_write(self):
        sid=self.flow()
        for quantity in [0,-1,1.5,True,'abc']:
            response=self.send('POST','/api/pedidos',{'id_sessao':sid,'itens':[{'id_prato':self.dish,'quantidade':quantity}]})
            self.assertEqual(response.status_code,400,response.json)
        self.assertEqual(self.send('POST','/api/itens-pedido',{}).status_code,405)
        self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(m.Pedido)),0)

    def test_reservation_cancel_frees_period(self):
        response=self.reserve()
        rid=response.json['reserva']['id_reserva']
        self.assertEqual(self.send('PATCH',f'/api/reservas/{rid}',{'status':'cancelada'}).status_code,200)
        self.assertEqual(self.reserve().status_code,201)

    def test_inactive_user_loses_session(self):
        self.login('admin@teste.com')
        response=self.send('PATCH',f'/api/usuarios/{self.customer}/status',{})
        self.assertEqual(response.status_code,200)
        response=self.cliente.post('/api/login',json={'email':'cliente@teste.com','senha':'senha1234'})
        self.assertEqual(response.status_code,401)


if __name__ == '__main__':
    unittest.main()
