"""Validated SQL-side search, filtering and bounded pagination."""
from datetime import datetime
from decimal import Decimal
from flask import request,g
from sqlalchemy import func,or_,select
from app.extensions import db
from app.controllers.http import date,fail,integer,number,text


def paginate(query,model):
    args=request.args
    page=integer(args.get('pagina','1'),'pagina')
    size=integer(args.get('limite','50'),'limite')
    if size>100:fail('O limite máximo é 100 registros.')
    columns=model.__table__.columns
    for key,value in args.items():
        if key in ('pagina','limite'):continue
        if key=='q':
            fields=[columns[name] for name in ('nome','email','descricao','bancada') if name in columns]
            if fields:query=query.where(or_(*(field.contains(text(value,'q',120),autoescape=True) for field in fields)))
            elif value:fail('Busca textual não disponível neste recurso.')
            continue
        if key=='situacao' and model.__tablename__=='pedido':
            if value not in ('ativos','finalizados'):fail('Situação inválida.')
            condition=model.status.in_(('entregue','cancelado'))
            query=query.where(condition if value=='finalizados' else ~condition);continue
        if key in ('de','ate') and 'criado_em' in columns:
            query=query.where(columns.criado_em>=date(value,key) if key=='de' else columns.criado_em<date(value,key));continue
        if key not in columns or key=='senha_hash':fail('Filtro não permitido: '+key)
        column=columns[key];kind=column.type.python_type
        if kind is bool:
            if value not in ('true','false','1','0'):fail('Filtro booleano inválido.')
            value=value in ('true','1')
        elif kind is int:value=integer(value,key)
        elif kind is Decimal:value=number(value,key,places=column.type.scale)
        elif kind is datetime:value=date(value,key)
        else:value=text(value,key,column.type.length)
        query=query.where(column==value)
    count=db.session.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    rows=list(db.session.scalars(query.offset((page-1)*size).limit(size)))
    mapping={'usuario':'usuarios','bancada':'bancadas','prato':'pratos','ingrediente':'ingredientes','reserva':'reservas','sessao':'sessoes','pedido':'pedidos','ficha_tecnica':'fichas_tecnicas','ingrediente_substituicao':'substituicoes','evento_auditoria':'eventos','movimentacao_estoque':'movimentacoes'}
    if not hasattr(g,'pagination'):g.pagination={}
    g.pagination[mapping.get(model.__tablename__,model.__tablename__) ]={'pagina':page,'limite':size,'total':count}
    return rows
