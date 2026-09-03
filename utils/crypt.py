from config import SECRET_KEY
from cryptography.fernet import Fernet
key = Fernet(SECRET_KEY)

def criptografar(texto): # criptografa o texto inserido como parametro, usando a criptografia AES.
    return key.encrypt(texto.encode()).decode()
def descriptografar(texto_criptografado): # descriptografa o texto inserido como parametro.
    return key.decrypt(texto_criptografado.encode()).decode()
