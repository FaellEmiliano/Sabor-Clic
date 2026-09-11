from config import Config

def criptografar(texto): # criptografa o texto inserido como parametro, usando a criptografia AES.
    texto = texto + Config.SECRET_KEY
    return texto
def descriptografar(texto_criptografado): # descriptografa o texto inserido como parametro.
    texto = texto_criptografado.replace(Config.SECRET_KEY, '')
    return texto
