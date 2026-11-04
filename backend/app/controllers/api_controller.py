"""HTTP contracts for authenticated operations and model-backed catalogs."""
from decimal import Decimal
from sqlalchemy import func
from app.controllers.consulta_controller import paginate
from app.controllers.http import date, password
from hashlib import sha256
import re
from secrets import token_urlsafe
from flask import g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app import models as m
from app.controllers import operacao_controller as op
from app.controllers import seguranca_controller as security
from app.controllers.http import fail, get, integer, number, owned, payload, permit, role, serial, text



def login():
    data = payload()
    email = text(data.get('email'), 'email', 180).lower()
    supplied_password = password(data.get('senha'))
    security.check_rate('login:'+email)
    user = m.Usuario_model.obter_usuario_email(email)
    if not user or not user.ativo or not check_password_hash(user.senha_hash, supplied_password):
        fail('Credenciais inválidas ou usuário inativo.', 401)
    if role(user) == 'desconhecido':
        fail('Usuário sem perfil de acesso.', 403)
    security.reset_rate('login:'+email)
    security.start_login(user)
    return jsonify(usuario=serial(user), csrf_token=session['csrf'])


def me():
    return jsonify(usuario=serial(g.user), csrf_token=session['csrf'])


def logout():
    security.end_login()
    return jsonify(mensagem='Sessão encerrada.')


def user_fields(data, create=False):
    allowed = {'nome', 'email', 'senha', 'endereco_entrega', 'turno', 'especialidade', 'ativo'}
    if set(data) - allowed:
        fail('Campos de usuário desconhecidos.')
    result = {}
    for key, maximum in [('nome',120), ('email',180), ('endereco_entrega',255), ('turno',50), ('especialidade',100)]:
        if key in data or (create and key in ('nome','email')):
            result[key] = text(data.get(key), key, maximum, required=key in ('nome','email'))
    if 'email' in result:
        result['email'] = result['email'].lower()
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', result['email']):
            fail('E-mail inválido.')
    if 'senha' in data or create:
        result['senha'] = password(data.get('senha'),minimum=8)
    if 'ativo' in data:
        if not isinstance(data['ativo'], bool):
            fail('ativo deve ser booleano.')
        result['ativo'] = data['ativo']
    return result


def create_user(tipo):
    if tipo not in ('cliente','cozinheiro','administrador'):
        fail('Perfil inválido.',404)
    if tipo != 'cliente':
        permit('administrador')
    data = user_fields(payload(), create=True)
    # Public registration cannot create privileged or inactive accounts.
    if tipo == 'cliente':
        security.check_rate('signup:'+str(request.remote_addr))
        allowed = {'nome','email','senha','endereco_entrega'}
        if set(data) - allowed:
            fail('Campos não permitidos no cadastro de cliente.')
    elif tipo == 'administrador' and set(data) & {'turno','especialidade','endereco_entrega'}:
        fail('Campos não pertencem ao perfil.')
    elif tipo == 'cozinheiro' and 'endereco_entrega' in data:
        fail('Campos não pertencem ao perfil.')
    creator = getattr(m.Usuario_model, 'inserir_' + tipo)
    result = creator(**data)
    return jsonify(usuario=serial(result.usuario)), 201


def users():
    permit('administrador')
    return jsonify(usuarios=[serial(u) for u in paginate(db.select(m.Usuario).order_by(m.Usuario.id_usuario),m.Usuario)])


def user(uid):
    if role() != 'administrador' and uid != g.user.id_usuario:
        fail('Registro não encontrado.',404)
    record = get(m.Usuario, uid)
    if request.method == 'GET':
        return jsonify(usuario=serial(record))
    if request.method == 'DELETE':
        permit('administrador')
        if uid == g.user.id_usuario:
            fail('Não exclua sua própria conta nesta sessão.',409)
        db.session.delete(record)
        db.session.commit()
        return jsonify(mensagem='Usuário excluído.')
    data = user_fields(payload())
    if not data:
        fail('Informe as alterações.')
    if role() != 'administrador' and 'ativo' in data:
        fail('Só administradores podem alterar a atividade.',403)
    if 'ativo' in data and not data['ativo'] and uid == g.user.id_usuario:
        fail('Não desative sua própria conta nesta sessão.',409)
    for field, value in data.items():
        if field == 'senha':
            record.senha_hash = generate_password_hash(value)
        elif field == 'endereco_entrega' and record.cliente:
            record.cliente.endereco_entrega = value
        elif field in ('turno','especialidade') and record.cozinheiro:
            setattr(record.cozinheiro, field, value)
        elif field in ('nome','email','ativo'):
            setattr(record, field, value)
        else:
            fail('Campo não pertence ao perfil.')
    db.session.commit()
    if uid == g.user.id_usuario:
        g.auth_session.versao_senha=security.fingerprint(record.senha_hash)
        db.session.commit()
    return jsonify(usuario=serial(record))


def user_status(uid):
    permit('administrador')
    record = get(m.Usuario,uid)
    if uid == g.user.id_usuario:
        fail('Não desative sua própria conta nesta sessão.',409)
    record.ativo = not record.ativo
    db.session.commit()
    return jsonify(usuario=serial(record))


def reservations():
    if request.method == 'GET':
        permit('cliente','administrador')
        return jsonify(reservas=filter_records(op.reservations()))
    return jsonify(reserva=serial(op.reserve(payload()))),201


def reservation(rid):
    permit('cliente','administrador')
    record = owned(get(m.Reserva,rid,lock=request.method!='GET'))
    if request.method == 'GET':
        return jsonify(reserva=serial(record))
    if request.method == 'DELETE':
        return jsonify(reserva=serial(op.reserve({'status':'cancelada'},record)))
    return jsonify(reserva=serial(op.reserve(payload(),record)))


def sessions():
    if request.method == 'GET':
        permit('cliente','administrador')
        return jsonify(sessoes=filter_records(op.sessions()))
    data = payload()
    if set(data) != {'id_reserva'}:
        fail('Informe apenas id_reserva; código e status são gerados pelo servidor.')
    return jsonify(sessao=serial(op.start_session(data))),201


def session_detail(sid):
    permit('cliente','administrador')
    record=owned(get(m.Sessao,sid))
    total=db.session.scalar(db.select(func.count()).select_from(m.Pedido).where(m.Pedido.id_sessao==sid))
    consumption=db.session.scalar(db.select(func.coalesce(func.sum(m.Pedido.valor_total),0)).where(m.Pedido.id_sessao==sid,m.Pedido.status!='cancelado'))
    return jsonify(sessao=serial(record),resumo={'pedidos':total,'consumo':float(consumption)})


def close_session(sid):
    return jsonify(sessao=serial(op.close_session(sid)))


def orders():
    if request.method == 'POST':
        return jsonify(pedido=op.order_json(op.checkout(payload()))),201
    records = op.orders()
    ids = {r['id_pedido'] for r in filter_records(records)}
    return jsonify(pedidos=[op.order_json(r) for r in records if r.id_pedido in ids])


def order(pid):
    if request.method == 'PATCH':
        return jsonify(pedido=op.order_json(op.update_order(pid,payload())))
    return jsonify(pedido=op.order_json(owned(get(m.Pedido,pid))))


def order_items():
    query=db.select(m.ItemPedido).join(m.Pedido,m.ItemPedido.id_pedido==m.Pedido.id_pedido).join(m.Sessao,m.Pedido.id_sessao==m.Sessao.id_sessao).join(m.Reserva,m.Sessao.id_reserva==m.Reserva.id_reserva)
    if role()=='cliente':query=query.where(m.Reserva.id_cliente==g.user.id_usuario)
    return jsonify(itens_pedido=[serial(r) for r in paginate(query.order_by(m.ItemPedido.id_item_pedido),m.ItemPedido)])


def order_item(iid):
    record = get(m.ItemPedido,iid)
    owned(get(m.Pedido,record.id_pedido))
    return jsonify(item_pedido=serial(record))


def kds():
    permit('administrador','cozinheiro')
    return jsonify(pedidos=[op.order_json(p) for p in op.orders(active_only=True) if p.status not in op.FINAL])


def reports():
    permit('administrador')
    filters=[];reserve_filters=[]
    for field,operator in [('de',lambda c,v:c>=v),('ate',lambda c,v:c<v)]:
        if request.args.get(field):
            value=date(request.args[field],field)
            filters.append(operator(m.Pedido.criado_em,value));reserve_filters.append(operator(m.Reserva.inicio,value))
    delivered=db.select(func.count(),func.coalesce(func.sum(m.Pedido.valor_total),0),func.coalesce(func.avg(m.Pedido.valor_total),0)).where(m.Pedido.status=='entregue',*filters)
    count,revenue,average=db.session.execute(delivered).one()
    total_orders=db.session.scalar(db.select(func.count()).select_from(m.Pedido).where(*filters))
    total_reservations=db.session.scalar(db.select(func.count()).select_from(m.Reserva).where(*reserve_filters))
    booking_revenue=db.session.scalar(db.select(func.coalesce(func.sum(m.Reserva.valor_total),0)).where(m.Reserva.status=='concluida',*reserve_filters))
    active=db.session.scalar(db.select(func.count()).select_from(m.Pedido).where(m.Pedido.status.not_in(op.FINAL),*filters))
    durations=list(db.session.execute(db.select(m.Pedido.preparo_em,m.Pedido.pronto_em).where(m.Pedido.preparo_em.is_not(None),m.Pedido.pronto_em.is_not(None),m.Pedido.status!='cancelado',*filters)))
    mean_time=sum((end-start).total_seconds()/60 for start,end in durations)/len(durations) if durations else None
    benches=db.session.execute(db.select(m.Bancada.id_bancada,m.Bancada.nome,func.count(m.Reserva.id_reserva),func.coalesce(func.sum(m.Reserva.valor_total),0)).outerjoin(m.Reserva,db.and_(m.Reserva.id_bancada==m.Bancada.id_bancada,m.Reserva.status=='concluida',*reserve_filters)).group_by(m.Bancada.id_bancada,m.Bancada.nome)).all()
    return jsonify(reservas=total_reservations,pedidos=total_orders,pedidos_entregues=count,receita_pedidos=float(revenue),ticket_medio=float(average),tempo_medio_preparo=mean_time,
        receita_reservas=float(booking_revenue),pedidos_ativos=active,
        bancadas_ativas=db.session.scalar(db.select(func.count()).select_from(m.Bancada).where(m.Bancada.ativa.is_(True))),
        por_bancada=[{'id_bancada':bid,'nome':name,'reservas':n,'receita':float(value)} for bid,name,n,value in benches])


def filter_records(records):
    return [serial(r) for r in records]


def cast_column(column,value,query=False):
    name = column.name
    kind = column.type.python_type
    if kind is bool:
        if query and value in ('true','false','1','0'):
            return value in ('true','1')
        if not isinstance(value,bool):
            fail(f'{name} deve ser booleano.')
        return value
    if kind is int:
        return integer(value,name)
    if kind is Decimal:
        minimum = Decimal('.001') if name == 'quantidade_necessaria' else Decimal('.0001') if name == 'fator_conversao' else Decimal('0')
        return number(value,name,minimum,places=column.type.scale)
    return text(value,name,column.type.length,required=not column.nullable)


CATALOGS = {
    'bancadas': (m.Bancada,'bancada',{'nome','descricao','valor_hora','ativa'}, {'nome','valor_hora'}),
    'pratos': (m.Prato,'prato',{'nome','descricao','preco','ativo'}, {'nome','preco'}),
    'ingredientes': (m.Ingrediente,'ingrediente',{'nome','unidade_medida','quantidade_estoque'}, {'nome','unidade_medida'}),
    'fichas-tecnicas': (m.FichaTecnica,'ficha_tecnica',{'id_prato','id_ingrediente','quantidade_necessaria'}, {'id_prato','id_ingrediente','quantidade_necessaria'}),
    'substituicoes': (m.SubstituicaoIngrediente,'substituicao',{'id_ingrediente_original','id_ingrediente_substituto','prioridade','fator_conversao'}, {'id_ingrediente_original','id_ingrediente_substituto'})
}


def catalog(resource, key=None):
    model, singular, allowed, required = CATALOGS[resource]
    if request.method == 'GET':
        if resource in ('ingredientes','fichas-tecnicas','substituicoes'):
            permit('administrador','cozinheiro')
        if key is not None:
            return jsonify({singular:serial(get(model,key))})
        records = paginate(db.select(model).order_by(*model.__table__.primary_key.columns),model)
        return jsonify({resource.replace('-','_'):filter_records(records)})
    if resource == 'pratos' and request.method == 'PATCH' and role() == 'cozinheiro':
        data = payload()
        if set(data) != {'ativo'}:
            fail('A cozinha só pode alterar a disponibilidade.',403)
    else:
        permit('administrador')
    record = get(model,key,lock=resource=='ingredientes') if key is not None else None
    if request.method == 'DELETE':
        if resource=='pratos':
            record.ativo=False;db.session.commit();return jsonify(prato=serial(record))
        db.session.delete(record)
        db.session.commit()
        return jsonify(mensagem='Registro excluído.')
    data = payload()
    if not data or set(data) - allowed:
        fail('Campos inválidos para este cadastro.')
    if record is None and required - set(data):
        fail('Campos obrigatórios: ' + ', '.join(sorted(required)))
    if record is not None and set(data) & set(model.__table__.primary_key.columns.keys()):
        fail('Não altere as chaves do registro.')
    values = {k:cast_column(model.__table__.columns[k],v) for k,v in data.items()}
    if resource == 'substituicoes' and (values.get('id_ingrediente_original',getattr(record,'id_ingrediente_original',None)) == values.get('id_ingrediente_substituto',getattr(record,'id_ingrediente_substituto',None))):
        fail('O substituto deve ser outro ingrediente.')
    for field, target in [('id_prato',m.Prato),('id_ingrediente',m.Ingrediente),('id_ingrediente_original',m.Ingrediente),('id_ingrediente_substituto',m.Ingrediente)]:
        if field in values:
            get(target,values[field])
    stock=values.pop('quantidade_estoque',None) if resource=='ingredientes' else None
    if record is None:
        if resource=='ingredientes': values['quantidade_estoque']=0
        record = model(**values)
        db.session.add(record)
    else:
        for field,value in values.items():
            setattr(record,field,value)
    db.session.flush()
    if stock is not None:
        from app.controllers.estoque_controller import movement
        db.session.refresh(record)
        delta=stock-record.quantidade_estoque
        movement(record.id_ingrediente,delta,'ajuste')
    db.session.commit()
    return jsonify({singular:serial(record)}),201 if key is None else 200



def audit():
    permit('administrador')
    query=db.select(m.EventoAuditoria).order_by(m.EventoAuditoria.id_evento.desc())
    return jsonify(eventos=[serial(row) for row in paginate(query,m.EventoAuditoria)])


def movements():
    permit('administrador','cozinheiro')
    query=db.select(m.MovimentacaoEstoque).order_by(m.MovimentacaoEstoque.id_movimentacao.desc())
    return jsonify(movimentacoes=[serial(row) for row in paginate(query,m.MovimentacaoEstoque)])


def availability():
    start=date(request.args.get('inicio'),'inicio');end=date(request.args.get('fim'),'fim')
    if end<=start:fail('Fim deve ser posterior ao início.')
    conflict=db.select(m.Reserva.id_bancada).where(m.Reserva.status.in_(('confirmada','em_andamento')),m.Reserva.inicio<end,m.Reserva.fim>start)
    rows=db.session.scalars(db.select(m.Bancada).where(m.Bancada.ativa.is_(True),m.Bancada.id_bancada.not_in(conflict)).order_by(m.Bancada.id_bancada))
    return jsonify(bancadas=[serial(r) for r in rows])


def kitchen_summary():
    permit('cozinheiro','administrador')
    counts=dict(db.session.execute(db.select(m.Pedido.status,func.count()).group_by(m.Pedido.status)).all())
    return jsonify(resumo={'ativos':sum(count for status,count in counts.items() if status not in op.FINAL),'entregues':counts.get('entregue',0),'em_preparo':counts.get('em_preparo',0)})
