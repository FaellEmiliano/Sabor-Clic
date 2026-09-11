from flask import Blueprint, request, session, jsonify
import re
import json
from app.model.usuario_model import Usuario_model

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
SENHA_REGEX = r'^(?=.*[A-Za-z])(?=.*\d).{8,}$'
auth_bp = Blueprint('auth', __name__)

def email_valido(email):
    if not isinstance(email, str):
        return False
    return bool(re.match(EMAIL_REGEX, email))
def senha_valida(senha):
    if not isinstance(senha, str):
        return False
    return bool(re.match(SENHA_REGEX, senha))
    

@auth_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify({'error': 'Nenhum dado JSON foi fornecido.'}), 400
    if isinstance(dados, str):
        dados = json.loads(dados)

    email = dados.get('email')
    senha = dados.get('senha')
    if not email or not senha:
        return jsonify({'erro': 'Email e senha são obrigatórios.'}), 400

    existe_user, id = Usuario_model.autenticar_usuario(email, senha)
    if not existe_user:
        return jsonify({'erro': 'Credenciais inválidas'}), 401
    usuario = Usuario_model.pegar_usuario(id)
    assert usuario is not None # pro pylance parar de chorar no meu ouvido.
    session.clear()
    session['usuario_id'] = usuario['id_usuario']
    session['usuario_nome'] = usuario['nome']
    return jsonify({
        'mensagem': 'Login efetuado com sucesso.',
        'usuario': {'nome': usuario['nome'], 'email': email}
    }), 200

@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()
    if not dados:
        return jsonify({'error': 'Nenhum dado JSON foi fornecido.'}), 400
    if isinstance(dados, str):
        dados = json.loads(dados)
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    if not email or not senha or not nome:
        return jsonify({'erro': 'Todos os dados precisam ser fornecidos (nome, email e senha).'}), 400
    if not email_valido(email) or not senha_valida(senha):
        return jsonify({'erro': 'Email e/ou senha invalido(s).'}), 400
    existe_email = Usuario_model.verificar_email_existente(email)
    if existe_email:
        return jsonify({'erro': 'Usuário com esse email já foi cadastrado.'}), 409
    Usuario_model.inserir_usuario(nome, email, senha)
    return jsonify({
        'mensagem':'Cadastro efetuado com sucesso'
    }), 200

@auth_bp.route('/usuarios/<id>', methods=['GET'])
def pegar_usuario(id):
    try:
        id_inteiro = int(id)
    except ValueError:
        return jsonify({'erro': 'ID fornecido é inválido.'}), 400
    usuario = Usuario_model.pegar_usuario(id_inteiro)
    if not usuario:
        return jsonify({'erro': 'Usuario não encontrado e/ou não existente.'}), 404
    return jsonify(dict(usuario))

@auth_bp.route('/usuarios/<id>/atualizar', methods=['POST'])
def atualizar_usuario(id):
    try:
        id_inteiro = int(id)
    except ValueError:
        return jsonify({'erro': 'ID fornecido é inválido.'}), 400
    usuario = Usuario_model.pegar_usuario(id_inteiro)
    if not usuario:
        return jsonify({'erro':'Usuario não encontrado e/ou não existente.'}), 404
    dados = request.get_json()
    if not dados:
        return jsonify({'error': 'Nenhum dado JSON foi fornecido.'}), 400
    if isinstance(dados, str):
        dados = json.loads(dados)
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    Usuario_model.atualizar_usuario(id_inteiro, nome, email, senha)
    return jsonify({'mensagem':'Usuario atualizado com sucesso.'}), 200


@auth_bp.route('/usuarios/<id>/deletar', methods=['DELETE'])
def deletar_usuario(id):
    try:
        id_inteiro = int(id)
    except ValueError:
        return jsonify({'erro': 'ID fornecido é inválido.'}), 400
    usuario = Usuario_model.pegar_usuario(id_inteiro)
    if not usuario:
        return jsonify({'erro': 'Usuario não encontrado e/ou não existente.'}), 404
    Usuario_model.deletar_usuario(id_inteiro)
    return jsonify({'mensagem':'Usuario deletado com sucesso.'}), 200
