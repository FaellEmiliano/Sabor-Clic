"""Persistent security sessions, rate limits, audit trail and stock ledger."""
from app.extensions import db

class SessaoAutenticacao(db.Model):
    __tablename__='sessao_autenticacao'
    id_sessao_auth=db.Column(db.String(64),primary_key=True)
    id_usuario=db.Column(db.Integer,db.ForeignKey('usuario.id_usuario',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,index=True)
    versao_senha=db.Column(db.String(64),nullable=False)
    criado_em=db.Column(db.DateTime,nullable=False)
    ultimo_acesso=db.Column(db.DateTime,nullable=False)
    expira_em=db.Column(db.DateTime,nullable=False)
    revogada=db.Column(db.Boolean,nullable=False,server_default=db.text('0'))

class LimiteAcesso(db.Model):
    __tablename__='limite_acesso'
    chave=db.Column(db.String(64),primary_key=True)
    inicio=db.Column(db.DateTime,nullable=False)
    tentativas=db.Column(db.Integer,nullable=False,server_default=db.text('0'))

class EventoAuditoria(db.Model):
    __tablename__='evento_auditoria'
    id_evento=db.Column(db.Integer,primary_key=True)
    id_usuario=db.Column(db.Integer,db.ForeignKey('usuario.id_usuario',ondelete='SET NULL',onupdate='CASCADE'))
    criado_em=db.Column(db.DateTime,nullable=False,index=True)
    acao=db.Column(db.String(12),nullable=False)
    recurso=db.Column(db.String(255),nullable=False)
    resultado=db.Column(db.Integer,nullable=False)
    correlacao=db.Column(db.String(64),nullable=False)

class MovimentacaoEstoque(db.Model):
    __tablename__='movimentacao_estoque'
    id_movimentacao=db.Column(db.Integer,primary_key=True)
    id_ingrediente=db.Column(db.Integer,db.ForeignKey('ingrediente.id_ingrediente',ondelete='RESTRICT',onupdate='CASCADE'),nullable=False,index=True)
    id_ingrediente_original=db.Column(db.Integer,db.ForeignKey('ingrediente.id_ingrediente',ondelete='RESTRICT',onupdate='CASCADE'))
    id_pedido=db.Column(db.Integer,db.ForeignKey('pedido.id_pedido',ondelete='RESTRICT',onupdate='CASCADE'),index=True)
    tipo=db.Column(db.String(20),nullable=False)
    quantidade=db.Column(db.Numeric(12,3),nullable=False)
    chave_evento=db.Column(db.String(100),nullable=False,unique=True)
    criado_em=db.Column(db.DateTime,nullable=False,server_default=db.func.current_timestamp())
    __table_args__=(db.CheckConstraint('quantidade <> 0',name='chk_movimento_quantidade'),)
