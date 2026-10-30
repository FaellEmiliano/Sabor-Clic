from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash

from app.models.usuario_model import (
    Usuario_model,
    Cliente_model,
    Cozinheiro_model,
    Administrador_model
)

class UsuarioController:
    @staticmethod
    def _serializar_usuario(usuario):
        """Método auxiliar interno para evitar repetição na montagem do dicionário (DRY)."""
        dados = {
            "id_usuario": usuario.id_usuario,
            "nome": usuario.nome,
            "email": usuario.email,
            "ativo": usuario.ativo,
        }

        if usuario.cliente:
            dados["tipo"] = "cliente"
            dados["endereco_entrega"] = usuario.cliente.endereco_entrega
        elif usuario.cozinheiro:
            dados["tipo"] = "cozinheiro"
            dados["turno"] = usuario.cozinheiro.turno
            dados["especialidade"] = usuario.cozinheiro.especialidade
        elif usuario.administrador:
            dados["tipo"] = "administrador"
        else:
            dados["tipo"] = "desconhecido"

        return dados

    @staticmethod
    def login(email, senha):
        if not email or not senha:
            return {"erro": "E-mail e senha são obrigatórios."}, 400

        usuario = Usuario_model.obter_usuario_email(email)

        # Valida se existe, checa o hash e confere se a atividade permite login
        if not usuario or not check_password_hash(usuario.senha_hash, senha) or not usuario.ativo:
            return {"erro": "Credenciais inválidas ou usuário inativo."}, 401

        return {
            "mensagem": "Login realizado com sucesso.",
            "usuario": UsuarioController._serializar_usuario(usuario),
        }, 200

    @staticmethod
    def cadastrar_cliente(nome, email, senha, endereco_entrega, ativo=True):
        if not nome or not email or not senha or not endereco_entrega:
            return {"erro": "Todos os campos obrigatórios devem ser preenchidos."}, 400

        try:
            novo_cliente = Usuario_model.inserir_cliente(nome, email, senha, endereco_entrega, ativo)
            return {
                "mensagem": "Cliente cadastrado com sucesso.",
                "usuario": UsuarioController._serializar_usuario(novo_cliente.usuario)
            }, 201
        except SQLAlchemyError:
            return {"erro": "Erro ao cadastrar. Verifique se o e-mail já está em uso."}, 409

    @staticmethod
    def cadastrar_cozinheiro(nome, email, senha, turno, especialidade, ativo=True):
        if not nome or not email or not senha or not turno or not especialidade:
            return {"erro": "Todos os campos obrigatórios devem ser preenchidos."}, 400

        try:
            novo_cozinheiro = Usuario_model.inserir_cozinheiro(nome, email, senha, turno, especialidade, ativo)
            return {
                "mensagem": "Cozinheiro cadastrado com sucesso.",
                "usuario": UsuarioController._serializar_usuario(novo_cozinheiro.usuario)
            }, 201
        except SQLAlchemyError:
            return {"erro": "Erro ao cadastrar. O e-mail pode já estar em uso."}, 409

    @staticmethod
    def cadastrar_administrador(nome, email, senha, ativo=True):
        if not nome or not email or not senha:
            return {"erro": "Todos os campos obrigatórios devem ser preenchidos."}, 400

        try:
            novo_admin = Usuario_model.inserir_administrador(nome, email, senha, ativo)
            return {
                "mensagem": "Administrador cadastrado com sucesso.",
                "usuario": UsuarioController._serializar_usuario(novo_admin.usuario)
            }, 201
        except SQLAlchemyError:
            return {"erro": "Erro ao cadastrar. O e-mail pode já estar em uso."}, 409

    @staticmethod
    def obter_por_id(id_usuario):
        usuario = Usuario_model.obter_usuario_id(id_usuario)
        if not usuario:
            return {"erro": "Usuário não encontrado."}, 404

        return {"usuario": UsuarioController._serializar_usuario(usuario)}, 200

    @staticmethod
    def obter_todos():
        usuarios = Usuario_model.obter_todos()
        # Aplica a serialização em todos os retornos do banco usando list comprehension
        return {"usuarios": [UsuarioController._serializar_usuario(u) for u in usuarios]}, 200

    @staticmethod
    def atualizar(id_usuario, **kwargs):
        usuario = Usuario_model.obter_usuario_id(id_usuario)
        if not usuario:
            return {"erro": "Usuário não encontrado."}, 404

        # Determina dinamicamente quais campos este usuário específico tem permissão para alterar
        campos_permitidos = set(Usuario_model.campos_atualizaveis) | {'senha'}
        if usuario.cliente:
            campos_permitidos |= set(Cliente_model.campos_atualizaveis)
        elif usuario.cozinheiro:
            campos_permitidos |= set(Cozinheiro_model.campos_atualizaveis)
        elif usuario.administrador:
            campos_permitidos |= set(Administrador_model.campos_atualizaveis)

        # Retorna erro imediatamente se o usuário tentar alterar campos que não pertencem ao perfil dele
        desconhecidos = set(kwargs.keys()) - campos_permitidos
        if desconhecidos:
            return {"erro": f"Campos inválidos ou não permitidos para este perfil: {', '.join(desconhecidos)}."}, 400

        try:
            # Separação e distribuição das requisições para cada model responsável
            campos_comuns = {k: v for k, v in kwargs.items() if k in Usuario_model.campos_atualizaveis}
            if campos_comuns:
                Usuario_model.atualizar_usuario(id_usuario, **campos_comuns)
                
            if 'senha' in kwargs:
                Usuario_model.atualizar_senha(id_usuario, kwargs['senha'])
                
            if usuario.cliente and 'endereco_entrega' in kwargs:
                Cliente_model.atualizar_cliente(id_usuario, endereco_entrega=kwargs['endereco_entrega'])
                
            campos_cozinheiro = {k: v for k, v in kwargs.items() if k in Cozinheiro_model.campos_atualizaveis}
            if usuario.cozinheiro and campos_cozinheiro:
                Cozinheiro_model.atualizar_cozinheiro(id_usuario, **campos_cozinheiro)
                
            return {"mensagem": "Dados atualizados com sucesso."}, 200
            
        except SQLAlchemyError:
            return {"erro": "Erro ao atualizar. Dados inválidos ou e-mail já em uso."}, 400

    @staticmethod
    def alternar_status_ativo(id_usuario):
        usuario = Usuario_model.obter_usuario_id(id_usuario)
        if not usuario:
            return {"erro": "Usuário não encontrado."}, 404

        estado_anterior = usuario.ativo
        
        try:
            Usuario_model.mudar_atividade(id_usuario)
            novo_status = "inativo" if estado_anterior else "ativo"
            return {"mensagem": f"Usuário alterado para {novo_status} com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Não foi possível alterar o status do usuário."}, 500

    @staticmethod
    def deletar(id_usuario):
        usuario = Usuario_model.obter_usuario_id(id_usuario)
        if not usuario:
            return {"erro": "Usuário não encontrado."}, 404

        try:
            Usuario_model.deletar_usuario(id_usuario)
            return {"mensagem": "Usuário deletado com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Erro ao deletar. Existem vínculos pendentes (ex: reservas) que impedem a exclusão."}, 409