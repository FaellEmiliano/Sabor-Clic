"""Database-backed session revocation and bounded authentication attempts."""
from datetime import timedelta
from hashlib import sha256
from secrets import token_urlsafe
from flask import current_app, g, request, session
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import SessaoAutenticacao, LimiteAcesso, EventoAuditoria
from app.controllers.http import fail, now


def fingerprint(value):
    return sha256(value.encode()).hexdigest()


def check_rate(identity):
    current=now()
    for value,limit in [('ip:'+str(request.remote_addr),current_app.config['LOGIN_IP_LIMIT']),(identity,current_app.config['LOGIN_LIMIT'])]:
        key=fingerprint(value)
        row=db.session.get(LimiteAcesso,key,with_for_update=True)
        if row is None:
            row=LimiteAcesso(chave=key,inicio=current,tentativas=0)
            db.session.add(row)
            try:
                db.session.flush()
            except IntegrityError:
                db.session.rollback()
                row=db.session.get(LimiteAcesso,key,with_for_update=True)
        if current-row.inicio >= timedelta(seconds=current_app.config['LOGIN_WINDOW_SECONDS']):
            row.inicio=current;row.tentativas=0
        if row.tentativas >= limit:
            db.session.rollback()
            fail('Muitas tentativas. Aguarde alguns minutos antes de tentar novamente.',429)
        row.tentativas+=1
        db.session.commit()


def reset_rate(identity):
    db.session.execute(db.update(LimiteAcesso).where(LimiteAcesso.chave==fingerprint(identity)).values(tentativas=0,inicio=now()))
    db.session.commit()


def start_login(user):
    old=session.get('sid')
    if old:
        row=db.session.get(SessaoAutenticacao,fingerprint(old))
        if row:row.revogada=True
    session.clear()
    sid=token_urlsafe(32)
    current=now()
    db.session.add(SessaoAutenticacao(id_sessao_auth=fingerprint(sid),id_usuario=user.id_usuario,
        versao_senha=fingerprint(user.senha_hash),criado_em=current,ultimo_acesso=current,
        expira_em=current+timedelta(hours=8),revogada=False))
    db.session.commit()
    session.update(uid=user.id_usuario,sid=sid,csrf=token_urlsafe(32))
    session.permanent=True


def authenticated(user):
    sid=session.get('sid')
    row=db.session.get(SessaoAutenticacao,fingerprint(sid)) if sid else None
    current=now()
    if not row or row.revogada or row.id_usuario!=user.id_usuario or row.versao_senha!=fingerprint(user.senha_hash) or row.expira_em<=current:
        return False
    if current-row.ultimo_acesso>timedelta(minutes=current_app.config['SESSION_IDLE_MINUTES']):
        row.revogada=True;db.session.commit();return False
    # Avoid a write and transaction on every GET.
    if current-row.ultimo_acesso>timedelta(minutes=1):
        row.ultimo_acesso=current;db.session.commit()
    g.auth_session=row
    return True


def end_login():
    sid=session.get('sid')
    row=db.session.get(SessaoAutenticacao,fingerprint(sid)) if sid else None
    if row:row.revogada=True;db.session.commit()
    session.clear()


def record_audit(response):
    if not request.path.startswith('/api') or request.method=='OPTIONS' or (request.method in ('GET','HEAD') and response.status_code<400):
        return response
    if response.status_code>=500:return response
    try:
        user=getattr(g,'user',None)
        db.session.add(EventoAuditoria(id_usuario=user.id_usuario if user else session.get('uid'),
            criado_em=now(),acao=request.method,recurso=request.path[:255],resultado=response.status_code,
            correlacao=g.request_id))
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.error('Falha ao registrar auditoria; correlation=%s',g.request_id)
    return response
