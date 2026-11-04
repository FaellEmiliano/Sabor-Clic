"""Transactional stock ledger; balances are updated by the backend on every database."""
from collections import defaultdict
from decimal import Decimal, ROUND_CEILING
from uuid import uuid4
from sqlalchemy import select, update
from app.extensions import db
from app import models as m
from app.controllers.http import fail, get


def movement(ingredient,quantity,kind,order_id=None,original_id=None,event=None):
    quantity=Decimal(quantity).quantize(Decimal('.001'))
    if not quantity:return
    row=m.MovimentacaoEstoque(id_ingrediente=ingredient,id_ingrediente_original=original_id,
        id_pedido=order_id,tipo=kind,quantidade=quantity,chave_evento=event or str(uuid4()))
    result=db.session.execute(update(m.Ingrediente).where(m.Ingrediente.id_ingrediente==ingredient,
        m.Ingrediente.quantidade_estoque+quantity>=0).values(quantidade_estoque=m.Ingrediente.quantidade_estoque+quantity),
        execution_options={'synchronize_session':False})
    if result.rowcount!=1:fail('Estoque insuficiente para concluir a operação.',409)
    db.session.add(row);db.session.flush()
    record=db.session.get(m.Ingrediente,ingredient)
    if record:db.session.expire(record,['quantidade_estoque'])


def allocate(prepared):
    """Aggregate the whole order first; only direct authorized substitutes are considered."""
    requirements=defaultdict(Decimal)
    for dish,quantity,_ in prepared:
        for recipe in db.session.scalars(select(m.FichaTecnica).where(m.FichaTecnica.id_prato==dish.id_prato)):
            requirements[recipe.id_ingrediente]+=recipe.quantidade_necessaria*quantity
    alternatives=list(db.session.scalars(select(m.SubstituicaoIngrediente).where(
        m.SubstituicaoIngrediente.id_ingrediente_original.in_(list(requirements))).order_by(
        m.SubstituicaoIngrediente.prioridade,m.SubstituicaoIngrediente.id_ingrediente_substituto))) if requirements else []
    ids=set(requirements)|{s.id_ingrediente_substituto for s in alternatives}
    ingredients=list(db.session.scalars(select(m.Ingrediente).where(m.Ingrediente.id_ingrediente.in_(sorted(ids)))
        .order_by(m.Ingrediente.id_ingrediente).with_for_update().execution_options(populate_existing=True))) if ids else []
    available={i.id_ingrediente:i.quantidade_estoque for i in ingredients}
    pending=[];result=[]
    for original,required in sorted(requirements.items()):
        required=required.quantize(Decimal('.001'),rounding=ROUND_CEILING)
        if available.get(original,0)>=required:
            available[original]-=required;result.append((original,original,required))
        else:pending.append((original,required))
    for original,required in pending:
        for alternative in alternatives:
            if alternative.id_ingrediente_original!=original:continue
            amount=(required*alternative.fator_conversao).quantize(Decimal('.001'),rounding=ROUND_CEILING)
            substitute=alternative.id_ingrediente_substituto
            if available.get(substitute,0)>=amount:
                available[substitute]-=amount;result.append((substitute,original,amount));break
        else:fail(f'Estoque insuficiente para o ingrediente #{original} e seus substitutos.',409)
    return result


def consume(order_id,allocations):
    for ingredient,original,quantity in sorted(allocations):
        movement(ingredient,-quantity,'consumo',order_id,original,f'consumo:{order_id}:{original}')


def restock(order_id):
    records=list(db.session.scalars(select(m.MovimentacaoEstoque).where(
        m.MovimentacaoEstoque.id_pedido==order_id,m.MovimentacaoEstoque.tipo=='consumo').order_by(m.MovimentacaoEstoque.id_ingrediente)))
    for row in records:
        get(m.Ingrediente,row.id_ingrediente,lock=True)
        movement(row.id_ingrediente,-row.quantidade,'estorno',order_id,row.id_ingrediente_original,
                 f'estorno:{order_id}:{row.id_ingrediente_original}')
