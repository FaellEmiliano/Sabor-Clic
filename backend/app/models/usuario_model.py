from copy import deepcopy


class UsuarioModel:
    _originais = [
        {"id": 1, "nome": "Rafael Gomes", "email": "rafael@exemplo.com", "perfil": "cliente"},
        {"id": 2, "nome": "Marina Souza", "email": "marina@saboreclic.com", "perfil": "cozinha"},
        {"id": 3, "nome": "Ana Martins", "email": "ana@saboreclic.com", "perfil": "admin"},
    ]
    _usuarios = deepcopy(_originais)

    @classmethod
    def reiniciar(cls):
        cls._usuarios = deepcopy(cls._originais)

    @classmethod
    def obter(cls, id_usuario):
        usuario = next((item for item in cls._usuarios if item["id"] == id_usuario), None)
        return deepcopy(usuario)

    @classmethod
    def obter_por_email(cls, email):
        email_normalizado = email.strip().lower()
        usuario = next(
            (item for item in cls._usuarios if item["email"].lower() == email_normalizado),
            None,
        )
        return deepcopy(usuario)

    @classmethod
    def criar(cls, nome, email, perfil):
        usuario = {
            "id": max((item["id"] for item in cls._usuarios), default=0) + 1,
            "nome": nome,
            "email": email.strip().lower(),
            "perfil": perfil,
        }
        cls._usuarios.append(usuario)
        return deepcopy(usuario)
