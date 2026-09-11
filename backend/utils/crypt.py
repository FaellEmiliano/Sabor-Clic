from config import Config
from cryptography.fernet import Fernet
assert Config.SECRET_KEY is not None
key = Fernet(Config.SECRET_KEY)

def criptografar(texto): # criptografa o texto inserido como parametro, usando a criptografia AES.
    return key.encrypt(texto.encode()).decode()
def descriptografar(texto_criptografado): # descriptografa o texto inserido como parametro.
    return key.decrypt(texto_criptografado.encode()).decode()
