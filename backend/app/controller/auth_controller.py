# Aqui ficam os endpoints de autentificação do site.

# .../api/cadastro
def cadastrar_cliente(dados):
    if dados:
        return True, 200 # Cada endpoint passa uma mensagem (devolvida em json normalmente), e um código do protocolo HTTP, sinalizando o que aconteceu na resposta da request
    return False, 401

# outros exemplos de endpoint:

# .../api/usuario/<int:id>
def get_usuario(id): # pega o usuario pelo id. Se o id não for um inteiro, o flask automáticamente já retorna o código 404 de página não encontrada no navegador.
    usuario = Usuario_model.get_usuario(id)
    return usuario

class Usuario_model:
    @staticmethod
    def get_usuario(id):
        pass

