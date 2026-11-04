import unittest
from decimal import Decimal
from datetime import timedelta,timezone
from uuid import uuid4
from app import models as m
from app.extensions import db
from app.controllers.http import now

class CompletionTestCase(unittest.TestCase):
    def setUp(self):
        from tests.test_api import ApiTestCase
        self.f=ApiTestCase();self.f.setUp()
    def tearDown(self):
        self.f.tearDown()
    def order(self,sid,key=None):
        return self.f.cliente.post('/api/pedidos',json={'id_sessao':sid,'itens':[{'id_prato':self.f.dish,'quantidade':2}]},headers={'X-CSRF-Token':self.f.csrf,'Idempotency-Key':key or str(uuid4())})
    def recipe(self,stock=10):
        ingredient=m.Ingrediente_model.inserir_ingrediente('Arroz','kg',stock)
        m.FichaTecnica_model.inserir_ficha_tecnica(self.f.dish,ingredient.id_ingrediente,Decimal('.5'))
        return ingredient.id_ingrediente
    def test_logout_revokes_copied_cookie(self):
        cookie=self.f.cliente.get_cookie('session').value
        self.f.send('POST','/api/logout',{})
        replay=self.f.app.test_client();replay.set_cookie('session',cookie)
        self.assertEqual(replay.get('/api/me').status_code,401)
    def test_rate_limit(self):
        for _ in range(6):
            r=self.f.cliente.post('/api/login',json={'email':'cliente@teste.com','senha':'errada'})
        self.assertEqual(r.status_code,429)
    def test_reject_reschedule_into_past(self):
        rid=self.f.reserve().json['reserva']['id_reserva']
        r=self.f.send('PATCH',f'/api/reservas/{rid}',{'inicio':(now()-timedelta(hours=2)).replace(tzinfo=timezone.utc).isoformat(),'fim':(now()-timedelta(hours=1)).replace(tzinfo=timezone.utc).isoformat()})
        self.assertEqual(r.status_code,400)
    def test_stock_consumption_and_restock(self):
        iid=self.recipe();sid=self.f.flow()
        r=self.order(sid);self.assertEqual(r.status_code,201,r.json)
        self.assertEqual(db.session.get(m.Ingrediente,iid).quantidade_estoque,Decimal('9'))
        self.f.login('admin@teste.com')
        r=self.f.send('PATCH',f"/api/pedidos/{r.json['pedido']['id_pedido']}",{'status':'cancelado'})
        self.assertEqual(r.status_code,200,r.json)
        self.assertEqual(db.session.get(m.Ingrediente,iid).quantidade_estoque,Decimal('10'))
    def test_insufficient_stock_rolls_back_order(self):
        iid=self.recipe(0);sid=self.f.flow()
        r=self.order(sid);self.assertEqual(r.status_code,409,r.json)
        self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(m.Pedido)),0)
    def test_substitute_consumption_is_recorded(self):
        original=self.recipe(0)
        substitute=m.Ingrediente_model.inserir_ingrediente('Quinoa','kg',10).id_ingrediente
        m.Substituicao_model.inserir_substituicao(original,substitute,1,2)
        r=self.order(self.f.flow());self.assertEqual(r.status_code,201,r.json)
        self.assertEqual(db.session.get(m.Ingrediente,substitute).quantidade_estoque,Decimal('8'))
        self.assertEqual(r.json['pedido']['consumos'][0]['id_ingrediente_original'],original)
    def test_checkout_idempotency(self):
        sid=self.f.flow();key=str(uuid4())
        first=self.order(sid,key);second=self.order(sid,key)
        self.assertEqual(second.status_code,201,second.json)
        self.assertEqual(first.json['pedido']['id_pedido'],second.json['pedido']['id_pedido'])
        self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(m.Pedido)),1)
    def test_audit_records_critical_operations(self):
        self.f.reserve();self.f.login('admin@teste.com')
        r=self.f.cliente.get('/api/auditoria')
        self.assertEqual(r.status_code,200,r.json)
        self.assertTrue(any(e['recurso']=='/api/reservas' for e in r.json['eventos']))


    def test_idempotency_key_cannot_change_payload(self):
        sid=self.f.flow();key=uuid4().hex
        self.assertEqual(self.order(sid,key).status_code,201)
        response=self.f.cliente.post('/api/pedidos',json={'id_sessao':sid,'itens':[{'id_prato':self.f.dish,'quantidade':1}]},headers={'X-CSRF-Token':self.f.csrf,'Idempotency-Key':key})
        self.assertEqual(response.status_code,409)
    def test_cancellation_after_preparation_does_not_restock(self):
        iid=self.recipe();r=self.order(self.f.flow());pid=r.json['pedido']['id_pedido']
        self.f.login('admin@teste.com')
        self.assertEqual(self.f.send('PATCH',f'/api/pedidos/{pid}',{'status':'em_preparo'}).status_code,200)
        self.assertEqual(self.f.send('PATCH',f'/api/pedidos/{pid}',{'status':'cancelado'}).status_code,200)
        self.assertEqual(db.session.get(m.Ingrediente,iid).quantidade_estoque,9)
    def test_expired_authentication_is_rejected(self):
        row=db.session.scalar(db.select(m.SessaoAutenticacao))
        row.expira_em=now()-timedelta(seconds=1);db.session.commit()
        self.assertEqual(self.f.cliente.get('/api/me').status_code,401)
    def test_paginated_catalog_and_report_period(self):
        self.f.login('admin@teste.com')
        m.Prato_model.inserir_prato('Segundo prato',20)
        response=self.f.cliente.get('/api/pratos?limite=1&pagina=2')
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json['pratos']),1)
        self.assertEqual(response.json['metadados']['pratos']['total'],2)
        self.assertEqual(self.f.cliente.get('/api/relatorios?de=2026-01-01&ate=2027-01-01').status_code,200)
        self.assertEqual(self.f.cliente.get('/api/pratos?limite=1000').status_code,400)
    def test_timezone_is_explicit_in_json(self):
        r=self.f.reserve()
        self.assertTrue(r.json['reserva']['inicio'].endswith('+00:00'))
    def test_shared_ingredient_is_aggregated_before_checkout(self):
        iid=self.recipe(Decimal('1.5'))
        another=m.Prato_model.inserir_prato('Outro prato',10)
        m.FichaTecnica_model.inserir_ficha_tecnica(another.id_prato,iid,1)
        sid=self.f.flow()
        response=self.f.send('POST','/api/pedidos',{'id_sessao':sid,'itens':[{'id_prato':self.f.dish,'quantidade':2},{'id_prato':another.id_prato,'quantidade':1}]})
        self.assertEqual(response.status_code,409)
        self.assertEqual(db.session.get(m.Ingrediente,iid).quantidade_estoque,Decimal('1.5'))
        self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(m.MovimentacaoEstoque)),0)

    def test_password_characters_are_not_trimmed(self):
        m.Usuario_model.inserir_administrador('Espaços','spaced@teste.com',' senha1234 ')
        response=self.f.cliente.post('/api/login',json={'email':'spaced@teste.com','senha':' senha1234 '})
        self.assertEqual(response.status_code,200,response.json)

if __name__=='__main__':unittest.main()
