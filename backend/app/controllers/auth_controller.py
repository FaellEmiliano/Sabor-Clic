from app.models.usuario_model import UsuarioModel

PERFIS = {"cliente", "cozinha", "admin"}


def obter_usuario(id_usuario):
    usuario = UsuarioModel.obter(id_usuario)
    if not usuario:
        return {"erro": "Usuário não encontrado."}, 404
    return {"usuario": usuario}, 200


def cadastrar_cliente(dados):
    nome = str(dados.get("nome", "")).strip()
    email = str(dados.get("email", "")).strip().lower()
    perfil = str(dados.get("perfil", "cliente")).strip().lower()

    if not nome or "@" not in email:
        return {"erro": "Informe nome e e-mail válido."}, 400
    if perfil not in PERFIS:
        return {"erro": "Perfil inválido."}, 400
    if UsuarioModel.obter_por_email(email):
        return {"erro": "Já existe um usuário com este e-mail."}, 409

    usuario = UsuarioModel.criar(nome, email, perfil)
    return {"mensagem": "Cadastro demonstrativo criado.", "usuario": usuario}, 201


def realizar_login(dados):
    email = str(dados.get("email", "")).strip().lower()
    senha = str(dados.get("senha", "")).strip()

    if not email or not senha:
        return {"erro": "Informe e-mail e senha."}, 400

    usuario = UsuarioModel.obter_por_email(email)
    if not usuario:
        return {"erro": "Usuário demonstrativo não encontrado."}, 401

    return {
        "mensagem": "Login demonstrativo realizado.",
        "usuario": usuario,
        "autenticacao": "simulada, sem cookie ou sessão de login",
    }, 200
