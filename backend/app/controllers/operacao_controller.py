"""Transactional application flows shared by the HTTP endpoints."""
from collections import Counter
from hashlib import sha256
import json
import re
from decimal import Decimal
from secrets import token_urlsafe
from flask import g, request
from sqlalchemy import select
from app.extensions import db
from app.controllers.consulta_controller import paginate
from app import models as m
from app.controllers.http import date, fail, get, integer, now, number, owned, permit, role, serial, text

ORDER_NEXT = {'recebido': 'em_preparo', 'em_preparo': 'pronto', 'pronto': 'entregue'}
FINAL = ('entregue', 'cancelado')


def reservations():
    query = select(m.Reserva).order_by(m.Reserva.inicio.desc())
    if role() == 'cliente':
        query = query.where(m.Reserva.id_cliente == g.user.id_usuario)
    return paginate(query,m.Reserva)


def reserve(data, record=None):
    permit('cliente', 'administrador')
    if record:
        owned(record)
        if record.status != 'confirmada':
            fail('Só é possível alterar uma reserva confirmada.', 409)
        if data.get('status') == 'cancelada':
            if set(data) != {'status'}:
                fail('Cancele a reserva em uma operação separada.')
            record.status = 'cancelada'
            db.session.commit()
            return record
    allowed = {'id_cliente', 'id_bancada', 'inicio', 'fim', 'status', 'valor_total'}
    if set(data) - allowed:
        fail('Campos de reserva desconhecidos.')
    if data.get('status', 'confirmada') != 'confirmada':
        fail('Status de reserva inválido.')
    uid = integer(data.get('id_cliente', record.id_cliente if record else g.user.id_usuario), 'id_cliente')
    if role() == 'cliente' and uid != g.user.id_usuario:
        fail('Não é permitido reservar para outro cliente.', 403)
    customer = get(m.Cliente, uid)
    if not customer.usuario.ativo: fail('Cliente inativo.',409)
    bid = integer(data.get('id_bancada', record.id_bancada if record else None), 'id_bancada')
    # All reservations on a bench serialize on this row, including concurrent requests.
    bench = get(m.Bancada, bid, lock=True)
    if not bench.ativa:
        fail('Bancada indisponível.', 409)
    start = date(data.get('inicio', record.inicio if record else None), 'inicio')
    end = date(data.get('fim', record.fim if record else None), 'fim')
    if end <= start or start < now():
        fail('Informe um período futuro com fim posterior ao início.')
    duration_hours = Decimal(str((end - start).total_seconds())) / Decimal('3600')
    total = (bench.valor_hora * duration_hours).quantize(Decimal('.01'))
    if total >= Decimal('100000000'):
        fail('O valor total da reserva excede o limite permitido. Escolha um período menor.')
    query = select(m.Reserva).where(m.Reserva.id_bancada == bid,
        m.Reserva.status.in_(('confirmada', 'em_andamento')),
        m.Reserva.inicio < end, m.Reserva.fim > start)
    if record:
        query = query.where(m.Reserva.id_reserva != record.id_reserva)
    if db.session.scalar(query.with_for_update()):
        fail('Esta bancada já está reservada neste período.', 409)
    if record is None:
        record = m.Reserva()
        db.session.add(record)
    record.id_cliente, record.id_bancada = uid, bid
    record.inicio, record.fim, record.status = start, end, 'confirmada'
    record.valor_total = total
    db.session.commit()
    return record


def sessions():
    query = select(m.Sessao).join(m.Reserva, m.Sessao.id_reserva == m.Reserva.id_reserva)
    if role() == 'cliente':
        query = query.where(m.Reserva.id_cliente == g.user.id_usuario)
    return paginate(query.order_by(m.Sessao.id_sessao.desc()),m.Sessao)


def start_session(data):
    permit('cliente', 'administrador')
    reservation = owned(get(m.Reserva, integer(data.get('id_reserva'), 'id_reserva'), lock=True))
    if reservation.status != 'confirmada':
        fail('A reserva não está confirmada.', 409)
    if now() >= reservation.fim:
        fail('O período desta reserva já terminou.', 409)
    if now() < reservation.inicio:
        fail('Aguarde o horário de início da reserva.', 409)
    if db.session.scalar(select(m.Sessao).where(m.Sessao.id_reserva == reservation.id_reserva)):
        fail('Já existe uma sessão para esta reserva.', 409)
    result = m.Sessao(id_reserva=reservation.id_reserva, codigo_acesso=token_urlsafe(18),
                     status='ativa', iniciado_em=now())
    reservation.status = 'em_andamento'
    db.session.add(result)
    db.session.commit()
    return result


def close_session(sid):
    permit('cliente', 'administrador')
    result = owned(get(m.Sessao, sid, lock=True))
    if result.status != 'ativa':
        fail('A sessão já está encerrada.', 409)
    if db.session.scalar(select(m.Pedido).where(m.Pedido.id_sessao == sid, m.Pedido.status.not_in(FINAL))):
        fail('Aguarde a conclusão dos pedidos antes de encerrar a sessão.', 409)
    result.status, result.encerrado_em = 'encerrada', now()
    get(m.Reserva, result.id_reserva).status = 'concluida'
    db.session.commit()
    return result


def order_json(order):
    result = serial(order)
    items = db.session.execute(select(m.ItemPedido,m.Prato.nome).join(m.Prato,m.ItemPedido.id_prato==m.Prato.id_prato).where(m.ItemPedido.id_pedido==order.id_pedido)).all()
    result['itens'] = [dict(serial(i), nome=i.nome_prato or name) for i,name in items]
    result['consumos'] = [serial(r) for r in db.session.scalars(select(m.MovimentacaoEstoque).where(m.MovimentacaoEstoque.id_pedido==order.id_pedido))]
    session = get(m.Sessao, order.id_sessao)
    reservation = get(m.Reserva, session.id_reserva)
    result['bancada'] = get(m.Bancada, reservation.id_bancada).nome
    return result


def orders(active_only=False):
    query = select(m.Pedido).join(m.Sessao, m.Pedido.id_sessao == m.Sessao.id_sessao).join(m.Reserva, m.Sessao.id_reserva == m.Reserva.id_reserva)
    if role() == 'cliente':
        query = query.where(m.Reserva.id_cliente == g.user.id_usuario)
    if active_only:query=query.where(m.Pedido.status.not_in(FINAL))
    return paginate(query.order_by(m.Pedido.id_pedido.asc() if active_only else m.Pedido.id_pedido.desc()),m.Pedido)


def checkout(data):
    permit('cliente', 'administrador')
    session = owned(get(m.Sessao, integer(data.get('id_sessao'), 'id_sessao'), lock=True))
    reservation = get(m.Reserva, session.id_reserva)
    key=request.headers.get('Idempotency-Key','')
    if not re.fullmatch(r'[a-zA-Z0-9_-]{16,64}',key):
        fail('Envie Idempotency-Key com 16 a 64 caracteres para confirmar o pedido.')
    items=data.get('itens')
    if not isinstance(items,list) or not items or len(items)>100:fail('Envie entre 1 e 100 itens no pedido.')
    counts=Counter()
    for item in items:
        if not isinstance(item,dict):fail('Item inválido.')
        counts[integer(item.get('id_prato'),'id_prato')]+=integer(item.get('quantidade'),'quantidade')
    address=text(data.get('endereco_entrega'),'endereco_entrega',required=False)
    notes=text(data.get('observacoes'),'observacoes',500,required=False)
    digest=sha256(json.dumps([session.id_sessao,sorted(counts.items()),address,notes],ensure_ascii=False).encode()).hexdigest()
    previous=db.session.scalar(select(m.Pedido).where(m.Pedido.id_sessao==session.id_sessao,m.Pedido.chave_idempotencia==key))
    if previous:
        if previous.hash_requisicao!=digest:fail('Esta chave já foi usada para outro conteúdo.',409)
        return previous
    if session.status!='ativa' or reservation.status!='em_andamento' or now()>=reservation.fim:
        fail('O pedido exige uma sessão ativa dentro do período reservado.',409)
    prepared = []
    total = Decimal('0')
    for pid, quantity in sorted(counts.items()):
        if quantity > 1000:
            fail('Quantidade máxima por prato: 1000.')
        dish = get(m.Prato, pid, lock=True)
        if not dish.ativo:
            fail(f'{dish.nome} está indisponível.', 409)
        subtotal = dish.preco * quantity
        total += subtotal
        prepared.append((dish, quantity, subtotal))
    from app.controllers.estoque_controller import allocate,consume
    allocations=allocate(prepared)
    # No commit until every line and stock movement is validated and inserted.
    order = m.Pedido(id_sessao=session.id_sessao, status='recebido', valor_total=number(total,'valor_total'),
                     endereco_entrega=address,observacoes=notes,chave_idempotencia=key,hash_requisicao=digest)
    db.session.add(order)
    db.session.flush()
    for dish, quantity, subtotal in prepared:
        db.session.add(m.ItemPedido(id_pedido=order.id_pedido, id_prato=dish.id_prato,
            quantidade=quantity, preco_unitario=dish.preco, subtotal=subtotal,nome_prato=dish.nome))
    db.session.flush()
    consume(order.id_pedido,allocations)
    db.session.commit()
    return order


def update_order(pid, data):
    permit('administrador', 'cozinheiro')
    order = get(m.Pedido, pid, lock=True)
    if not data or set(data) - {'status', 'tempo_estimado'}:
        fail('Só é permitido alterar status e tempo_estimado.')
    if 'status' in data:
        target = data['status']
        if target != ORDER_NEXT.get(order.status) and not (target == 'cancelado' and role() == 'administrador' and order.status not in FINAL):
            fail('Transição de status inválida.', 409)
        if target=='cancelado' and order.status=='recebido':
            from app.controllers.estoque_controller import restock
            restock(order.id_pedido)
        field={'em_preparo':'preparo_em','pronto':'pronto_em','entregue':'entregue_em','cancelado':'cancelado_em'}.get(target)
        if field:setattr(order,field,now())
        order.status = target
    if 'tempo_estimado' in data:
        order.tempo_estimado = integer(data['tempo_estimado'], 'tempo_estimado', 0)
    db.session.commit()
    return order
