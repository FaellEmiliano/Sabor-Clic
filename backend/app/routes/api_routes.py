"""Thin HTTP routing; business handlers live in controllers/api_controller.py."""
from functools import partial
from flask import Blueprint
from app.controllers import api_controller as c
from app.controllers.imagem_controller import images

api_bp=Blueprint('api',__name__,url_prefix='/api')
api_bp.add_url_rule('/imagens', 'images', images, methods=['GET', 'POST'])
api_bp.add_url_rule('/login','login',c.login,methods=['POST'])
api_bp.add_url_rule('/me','me',c.me,methods=['GET'])
api_bp.add_url_rule('/logout','logout',c.logout,methods=['POST'])
api_bp.add_url_rule('/usuarios/<tipo>','create_user',c.create_user,methods=['POST'])
api_bp.add_url_rule('/usuarios','users',c.users,methods=['GET'])
api_bp.add_url_rule('/usuarios/<int:uid>','user',c.user,methods=['GET', 'PATCH', 'DELETE'])
api_bp.add_url_rule('/usuarios/<int:uid>/status','user_status',c.user_status,methods=['PATCH'])
api_bp.add_url_rule('/reservas','reservations',c.reservations,methods=['GET', 'POST'])
api_bp.add_url_rule('/reservas/<int:rid>','reservation',c.reservation,methods=['GET', 'PATCH', 'DELETE'])
api_bp.add_url_rule('/sessoes','sessions',c.sessions,methods=['GET', 'POST'])
api_bp.add_url_rule('/sessoes/<int:sid>','session_detail',c.session_detail,methods=['GET'])
api_bp.add_url_rule('/sessoes/<int:sid>/encerrar','close_session',c.close_session,methods=['POST'])
api_bp.add_url_rule('/pedidos','orders',c.orders,methods=['GET', 'POST'])
api_bp.add_url_rule('/pedidos/<int:pid>','order',c.order,methods=['GET', 'PATCH'])
api_bp.add_url_rule('/itens-pedido','order_items',c.order_items,methods=['GET'])
api_bp.add_url_rule('/itens-pedido/<int:iid>','order_item',c.order_item,methods=['GET'])
api_bp.add_url_rule('/kds','kds',c.kds,methods=['GET'])
api_bp.add_url_rule('/relatorios','reports',c.reports,methods=['GET'])

for resource in c.CATALOGS:
    api_bp.add_url_rule('/'+resource,resource+'_list',partial(c.catalog,resource),methods=['GET','POST'])
    if resource not in ('fichas-tecnicas','substituicoes'):
        api_bp.add_url_rule('/'+resource+'/<int:key>',resource+'_detail',partial(c.catalog,resource),methods=['GET','PATCH','DELETE'])
api_bp.add_url_rule('/fichas-tecnicas/<int:pid>/ingredientes/<int:iid>','ficha_detail',lambda pid,iid:c.catalog('fichas-tecnicas',(pid,iid)),methods=['GET','PATCH','DELETE'])
api_bp.add_url_rule('/substituicoes/<int:oid>/substitutos/<int:sid>','sub_detail',lambda oid,sid:c.catalog('substituicoes',(oid,sid)),methods=['GET','PATCH','DELETE'])

api_bp.add_url_rule('/auditoria','audit',c.audit,methods=['GET'])
api_bp.add_url_rule('/movimentacoes','movements',c.movements,methods=['GET'])

api_bp.add_url_rule('/disponibilidade','availability',c.availability,methods=['GET'])

api_bp.add_url_rule('/resumo-cozinha','kitchen_summary',c.kitchen_summary,methods=['GET'])
