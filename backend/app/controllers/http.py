"""Shared HTTP validation, serialization and access control."""
import hmac
from hashlib import sha256
import re
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
from flask import abort, g, request, session
from app.extensions import db
from app.models import Usuario, Reserva, Sessao, Pedido


# Interrompe o atendimento e devolve ao navegador a mensagem e o código de erro informados.
# Por padrão, indica que os dados enviados são inválidos.
def fail(message, status=400):
    abort(status, description=message)


# Lê os dados enviados pelo navegador e exige um objeto JSON, um conjunto de campos com nome
# e valor.
def payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        fail('Envie um objeto JSON válido.')
    return data


# Aceita dígitos que representem um número inteiro dentro dos limites definidos e devolve o
# número convertido.
def integer(value, name='id', minimum=1):
    if isinstance(value, bool) or not re.fullmatch(r'\d+', str(value)):
        fail(f'{name} deve ser um inteiro maior ou igual a {minimum}.')
    value = int(value)
    if value < minimum or value > 2147483647:
        fail(f'{name} fora do intervalo permitido.')
    return value


# Confere se o valor é um decimal finito dentro do intervalo permitido e ajusta a quantidade
# de casas decimais.
def number(value, name, minimum=Decimal('0'), places=2):
    try:
        if isinstance(value, bool):
            raise ValueError()
        result = Decimal(str(value))
        if not result.is_finite() or result < minimum or result >= Decimal('100000000'):
            raise ValueError()
        return result.quantize(Decimal(1).scaleb(-places))
    except (ValueError, InvalidOperation, TypeError):
        fail(f'{name} deve ser um número válido maior ou igual a {minimum}.')


# Confere se o campo é texto, se foi preenchido quando obrigatório e se cabe no tamanho
# permitido. Retira espaços do começo e do fim.
def text(value, name, maximum=255, required=True):
    if value is None and not required:
        return None
    if not isinstance(value, str) or (required and not value.strip()) or len(value) > maximum:
        fail(f'{name} inválido (máximo {maximum} caracteres).')
    return value.strip()


# Confere o tamanho da senha e rejeita valores vazios. Devolve a senha exatamente como foi
# digitada, inclusive com espaços nas pontas.
def password(value,minimum=1):
    if not isinstance(value,str) or not value.strip() or len(value)<minimum or len(value)>255:
        fail(f'A senha deve ter entre {minimum} e 255 caracteres.')
    return value


# Interpreta uma data no formato ISO. Quando o texto não traz fuso horário, usa UTC−3.
# Converte o horário de texto para UTC, como são guardadas as datas no banco.
def date(value, name):
    try:
        if isinstance(value,datetime):return value
        result=datetime.fromisoformat(value.replace('Z','+00:00'))
        if result.tzinfo is None:result=result.replace(tzinfo=timezone(timedelta(hours=-3)))
        return result.astimezone(timezone.utc).replace(tzinfo=None)
    except (ValueError,TypeError,AttributeError):
        fail(f'{name} deve estar em formato ISO 8601.')


# Devolve o instante atual em UTC no formato de data usado pelo banco.
def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# Transforma um registro em campos que o navegador consegue ler. Omite o código derivado da
# senha, inclui o fuso nas datas e acrescenta dados específicos do perfil de usuário.
def serial(record):
    result = {}
    for column in record.__table__.columns:
        if column.name == 'senha_hash':
            continue
        value = getattr(record, column.name)
        result[column.name] = value.replace(tzinfo=timezone.utc).isoformat() if isinstance(value, datetime) else float(value) if isinstance(value, Decimal) else value
    if isinstance(record, Usuario):
        result['tipo'] = role(record)
        if record.cliente:
            result['endereco_entrega'] = record.cliente.endereco_entrega
        if record.cozinheiro:
            result.update(turno=record.cozinheiro.turno, especialidade=record.cozinheiro.especialidade)
    return result


# Identifica o perfil da conta pelos vínculos cadastrados e usa a conta da requisição atual
# quando nenhuma é passada.
def role(user=None):
    user = user or g.user
    if user.administrador:
        return 'administrador'
    if user.cozinheiro:
        return 'cozinheiro'
    return 'cliente' if user.cliente else 'desconhecido'


# Confere se a conta atual tem um dos perfis autorizados. Interrompe a operação com erro de
# permissão se não tiver.
def permit(*roles):
    if role() not in roles:
        fail('Você não tem permissão para esta operação.', 403)


# Procura um registro pela identificação e informa que ele não foi encontrado quando estiver
# ausente. Quando solicitado, pede ao banco que bloqueie a linha durante a operação.
def get(model, key, lock=False):
    record = db.session.get(model, key, with_for_update=lock)
    if record is None:
        fail('Registro não encontrado.', 404)
    return record


# Para clientes, segue os vínculos de pedido e sessão até a reserva e confirma que ela
# pertence à conta atual. Trata registros de outros clientes como inexistentes.
def owned(record):
    if role() == 'cliente':
        reserve = record
        if isinstance(record, Pedido):
            reserve = get(Sessao, record.id_sessao)
        if isinstance(reserve, Sessao):
            reserve = get(Reserva, reserve.id_reserva)
        if reserve.id_cliente != g.user.id_usuario:
            fail('Registro não encontrado.', 404)
    return record


# Libera as rotas públicas e verifica conta ativa, sessão válida e perfil para o restante da
# API. Em alterações, confere também o código CSRF, que ajuda a impedir pedidos forjados por
# outros sites.
def protect():
    if not request.path.startswith('/api') or request.method == 'OPTIONS' or request.path == '/api':
        return
    if request.path == '/api/login' or (request.path == '/api/usuarios/cliente' and request.method == 'POST'):
        return
    from app.controllers.seguranca_controller import authenticated
    uid = session.get('uid')
    g.user = db.session.get(Usuario, uid) if uid else None
    if not g.user or not g.user.ativo or not authenticated(g.user):
        session.clear()
        fail('Faça login para continuar.', 401)
    if role() == 'desconhecido':
        fail('Usuário sem perfil de acesso.', 403)
    if request.method not in ('GET', 'HEAD'):
        token = request.headers.get('X-CSRF-Token', '')
        if not token or not hmac.compare_digest(token, session.get('csrf', '')):
            fail('Token de sessão inválido. Entre novamente.', 403)
